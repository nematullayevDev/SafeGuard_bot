"""SafeGuard Bot — entry point."""
import asyncio
import logging
import os

from aiohttp import web
from aiogram.webhook.aiohttp_impl import SimpleRequestHandler, setup_application

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


async def main() -> None:
    setup_logging()
    init_schema()
    container = build_container()
    register_all(dp, container)

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
        await bot.set_webhook(webhook_target)
        logger.info(f"🚀 Webhook muvaffaqiyatli o'rnatildi: {webhook_target}")
        logger.info(f"⚡ Bot {port}-portda so'rovlarni qabul qilmoqda!")
        
        # Jarayonni cheksiz kutish rejimida ushlab turamiz
        await asyncio.Event().wait()
    else:
        # Standart Polling rejimi
        if os.getenv("PORT"):
            asyncio.create_task(start_health_check_server())

        logger.info("✅ SafeGuard Bot polling rejimida ishga tushdi!")
        # Eski webhookni tozalash
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
