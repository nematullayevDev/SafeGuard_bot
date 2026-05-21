"""Mass-message broadcasting with progress callback."""
import asyncio
import logging
from typing import Awaitable, Callable

from aiogram import Bot

from app.repositories import UserRepository

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], Awaitable[None]]


class BroadcastService:
    def __init__(self, bot: Bot, user_repo: UserRepository) -> None:
        self._bot = bot
        self._users = user_repo

    async def send(self, text: str, on_progress: ProgressCallback | None = None,
                   delay_seconds: float = 0.05) -> tuple[int, int]:
        ids = self._users.all_ids()
        sent = 0
        failed = 0
        for i, uid in enumerate(ids, 1):
            try:
                await self._bot.send_message(uid, text, parse_mode="HTML")
                sent += 1
            except Exception:
                failed += 1
            if on_progress and i % 20 == 0:
                try:
                    await on_progress(i, len(ids))
                except Exception as e:
                    logger.debug("progress callback xato: %s", e)
            await asyncio.sleep(delay_seconds)
        return sent, failed
