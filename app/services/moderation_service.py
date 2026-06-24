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
                          sender_name: str, reason: str, max_warns: int = None) -> None:
        count = self._warnings.add(chat_id, user_id, reason)
        mention = f'<a href="tg://user?id={user_id}">{sender_name}</a>'
        limit = max_warns if max_warns is not None else self._max

        if count >= limit:
            try:
                await self._bot.ban_chat_member(chat_id, user_id)
                self._warnings.clear(chat_id, user_id)
                await self._bot.send_message(
                    chat_id,
                    f"🚫 {mention} <b>BAN</b> qilindi! ({limit} ta warn)\nSabab: {reason}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Ban qilib bo'lmadi: %s", e)
        else:
            await self._bot.send_message(
                chat_id,
                f"⚠️ {mention} ogohlantirish oldi! Warn: {count}/{limit}\nSabab: {reason}",
                parse_mode="HTML",
            )
