"""SafeGuard Bot — entry point."""
import asyncio
import logging
import os

from aiohttp import web
# TUZATILDI: aiohttp_impl o'rniga aiohttp_server ishlatildi
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.container import build_container
from app.controllers import register_all
from app.core.bot import bot, dp
from app.core.logger import setup_logging
from app.repositories import init_schema

logger = logging.getLogger(__name__)


async def health_check(request: web.Request) -> web.Response:
    """Respond to health checks from platforms like Render or Koyeb."""
    return web.Response(text="Bot is running!")


async def start_health_check_server() -> None:
    """Start a minimal HTTP server to satisfy port binding requirements on free servers in polling mode."""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🚀 Dummy server {port}-portda ishga tushdi!")


async def self_ping(url: str, interval: int = 600) -> None:
    """Periodically pings the health check endpoint to prevent Render from sleeping."""
    await asyncio.sleep(30)  # Wait 30s to let the server start fully
    logger.info(f"Self-ping xizmati ishga tushdi: {url}")
    import aiohttp
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Ping the health check endpoint
                async with session.get(url, timeout=15) as resp:
                    logger.info(f"Self-ping muvaffaqiyatli: status={resp.status}")
            except Exception as e:
                logger.warning(f"Self-pingda xatolik: {e}")
            await asyncio.sleep(interval)


from aiogram.types import BotCommand


async def set_bot_commands() -> None:
    """Set up the official Telegram commands menu list."""
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="menu", description="📱 Bosh menyuni ochish"),
        BotCommand(command="quiz", description="🛡️ Kiber-Savodxonlik Viktorinasi"),
    ]

    try:
        await bot.set_my_commands(commands)
        logger.info("✅ Bot buyruqlari muvaffaqiyatli o'rnatildi!")
    except Exception as e:
        logger.warning(f"Bot buyruqlarini o'rnatishda xatolik: {e}")


async def main() -> None:
    setup_logging()
    init_schema()
    container = build_container()

    # Register subscription middleware
    from app.core.middlewares import SubscriptionMiddleware
    dp.message.outer_middleware(SubscriptionMiddleware(container))
    dp.callback_query.outer_middleware(SubscriptionMiddleware(container))

    register_all(dp, container)

    # Fonda ishlovchi rejalashtirgichni ishga tushirish (daily backup + tips)
    from app.services.scheduler import start_scheduler
    start_scheduler(bot, container)
    
    # Bot buyruqlari menyusini ro'yxatdan o'tkazamiz
    await set_bot_commands()


    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        # Render.com yoki boshqa serverlar uchun Webhook rejimi
        logger.info("🔧 Webhook rejimi faollashtirilmoqda...")
        app = web.Application()
        app.router.add_get("/", health_check)
        
        # Webhook handlerni ro'yxatdan o'tkazish
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        port = int(os.getenv("PORT", 8080))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        
        # Telegram webhookni sozlash
        webhook_target = f"{webhook_url.rstrip('/')}/webhook"
        try:
            await bot.set_webhook(webhook_target)
            logger.info(f"🚀 Webhook muvaffaqiyatli o'rnatildi: {webhook_target}")
        except Exception as e:
            logger.error(f"❌ Telegram Wpebhook-ni sozlashda xatolik: {e}")
            
        logger.info(f"⚡ Bot {port}-portda so'rovlarni qabul qilmoqda!")
        
        # Render serverini uyg'oq ushlab turish uchun o'z-o'zini ping qilish xizmati
        asyncio.create_task(self_ping(webhook_url))
        
        # Jarayonni cheksiz kutish rejimida ushlab turamiz
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            pass
        finally:
            logger.info("🧹 Webhook serveri yopilmoqda, resurslar tozalanmoqda...")
            try:
                await bot.delete_webhook()
            except Exception as e:
                logger.warning(f"Webhook o'chirishda xatolik: {e}")
            await container.vt.close()
            await runner.cleanup()
    else:
        # Standart Polling rejimi
        server_runner = None
        if os.getenv("PORT"):
            port = int(os.getenv("PORT", 8080))
            app = web.Application()
            app.router.add_get("/", health_check)
            server_runner = web.AppRunner(app)
            await server_runner.setup()
            site = web.TCPSite(server_runner, "0.0.0.0", port)
            await site.start()
            logger.info(f"🚀 Dummy server {port}-portda ishga tushdi!")

        logger.info("✅ SafeGuard Bot polling rejimida ishga tushdi!")
        # Eski webhookni tozalash va eski kelib qolgan so'rovlarni o'chirish
        await bot.delete_webhook(drop_pending_updates=True)
        try:
            await dp.start_polling(
                bot,
                allowed_updates=[
                    "message", "callback_query", "my_chat_member",
                    "chat_member", "inline_query"
                ]
            )
        finally:
            await container.vt.close()
            if server_runner:
                logger.info("🧹 Dummy polling serveri tozalanmoqda...")
                await server_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")