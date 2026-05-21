"""SafeGuard Bot — entry point."""
import asyncio
import logging
import os

from aiohttp import web

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
    """Start a minimal HTTP server to satisfy port binding requirements on free servers."""
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

    # Free serverlarda port binding muammosini hal qilish uchun dummy serverni ishga tushiramiz
    if os.getenv("PORT"):
        asyncio.create_task(start_health_check_server())

    logger.info("✅ SafeGuard Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
