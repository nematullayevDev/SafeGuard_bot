"""Custom aiogram filters and shared helpers."""
import logging

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.container import Container
from app.core.bot import bot
from app.core.config import settings
from app.views.keyboards import go_start_kb

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    """User is the bot owner."""

    async def __call__(self, event) -> bool:
        uid = event.from_user.id if event.from_user else 0
        return uid == settings.admin_id


def is_owner(event) -> bool:
    uid = getattr(event.from_user, "id", 0) if event.from_user else 0
    return uid == settings.admin_id


async def is_chat_admin(message: Message) -> bool:
    """User is admin/creator of the group."""
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        logger.warning("get_chat_member xato: %s", e)
        return False


async def ensure_registered(message: Message, container: Container) -> bool:
    if container.users.is_registered(message.from_user.id):
        return True
    lang = container.users.get_language(message.from_user.id)
    from app.views.texts import get_text
    await message.answer(get_text("register_first", lang), reply_markup=go_start_kb(lang))
    return False


async def deny_if_not_owner(call: CallbackQuery) -> bool:
    if not is_owner(call):
        from app.views.texts import get_text
        from app.repositories.base import get_conn
        
        lang = "uz"
        try:
            with get_conn() as conn:
                row = conn.execute("SELECT language FROM users WHERE user_id = ?", (call.from_user.id,)).fetchone()
                if row and row[0]:
                    lang = row[0]
        except Exception:
            pass
            
        await call.answer(get_text("admin_only_alert", lang), show_alert=True)
        return True
    return False
