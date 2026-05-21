"""Warn/ban moderation flow for groups."""
import logging

from aiogram import Bot

from app.repositories import WarningRepository

logger = logging.getLogger(__name__)


class ModerationService:
    def __init__(self, bot: Bot, warning_repo: WarningRepository,
                 max_warnings: int) -> None:
        self._bot = bot
        self._warnings = warning_repo
        self._max = max_warnings

    async def warn_or_ban(self, chat_id: int, user_id: int,
                          sender_name: str, reason: str) -> None:
        count = self._warnings.add(chat_id, user_id, reason)
        mention = f'<a href="tg://user?id={user_id}">{sender_name}</a>'

        if count >= self._max:
            try:
                await self._bot.ban_chat_member(chat_id, user_id)
                self._warnings.clear(chat_id, user_id)
                await self._bot.send_message(
                    chat_id,
                    f"🚫 {mention} <b>BAN</b> qilindi! ({self._max} ta warn)\nSabab: {reason}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Ban qilib bo'lmadi: %s", e)
        else:
            await self._bot.send_message(
                chat_id,
                f"⚠️ {mention} ogohlantirish oldi! Warn: {count}/{self._max}\nSabab: {reason}",
                parse_mode="HTML",
            )
