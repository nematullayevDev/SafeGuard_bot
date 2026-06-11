"""Middleware to enforce mandatory registration and channel subscription check in private chats."""
import logging
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.container import Container
from app.core.config import settings
from app.core.bot import bot
from app.views.keyboards import channel_subscribe_kb, go_start_kb
from app.views.texts import (
    CHANNEL_SUBSCRIBE_REQUIRED,
    CHANNEL_SUBSCRIBE_FAIL_ALERT,
    REGISTER_FIRST,
)

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    # Class-level cache shared across middleware instances: user_id -> (is_subscribed, expiry_time)
    cache: Dict[int, tuple[bool, float]] = {}
    cache_ttl: float = 60.0  # 1 minute Time-To-Live for fast status updates

    def __init__(self, container: Container) -> None:
        self.container = container
        super().__init__()

    async def _is_subscribed(self, user_id: int) -> bool:
        """Check if user is subscribed, using a short TTL cache to prevent Telegram API rate limits."""
        now = time.time()
        if user_id in self.cache:
            is_sub, expiry = self.cache[user_id]
            if now < expiry:
                return is_sub

        channel = settings.channel_id if settings.channel_id else settings.channel_username
        if not channel:
            logger.info("Majburiy obuna O'CHIRILGAN — CHANNEL_ID/CHANNEL_USERNAME sozlanmagan.")
            return True

        try:
            member = await bot.get_chat_member(channel, user_id)
            subscribed = member.status not in ("left", "kicked")
            # Cache the result
            self.cache[user_id] = (subscribed, now + self.cache_ttl)
            logger.debug("Obuna tekshiruvi (API): user=%s, sub=%s", user_id, subscribed)
            return subscribed
        except Exception as e:
            logger.warning(
                "Kanal obuna tekshirishda XATOLIK [channel=%s, user=%s]: %s | "
                "Hozircha foydalanuvchiga ruxsat berildi (bloklanmadi).",
                channel, user_id, e,
            )
            # Fallback to True so the bot does not break if Telegram API fails or bot is not admin yet
            return True

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        chat = None
        user = None

        if isinstance(event, Message):
            chat = event.chat
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            chat = event.message.chat if event.message else None
            user = event.from_user

        # Enforce check only in private chats
        if chat and chat.type == "private" and user:
            # Check bypass for start/register commands and check_subscription verification callbacks
            is_bypass = False
            if isinstance(event, Message) and event.text:
                parts = event.text.split()
                if parts and parts[0] == "/start":
                    is_bypass = True
            elif isinstance(event, CallbackQuery) and event.data in ("go_start", "check_subscription"):
                is_bypass = True

            # Get current FSM state (e.g. if the user is in waiting_phone registration state)
            state = data.get("state")
            state_str = await state.get_state() if state else None
            is_registering = state_str == "Registration:waiting_phone"

            # If not in registration flow or bypass:
            if not is_bypass and not is_registering:
                # 1. Check if user is registered in database
                is_registered = self.container.users.is_registered(user.id)
                if not is_registered:
                    # Unregistered user trying to click old buttons or send messages
                    if isinstance(event, Message):
                        await event.answer(REGISTER_FIRST, reply_markup=go_start_kb())
                    elif isinstance(event, CallbackQuery):
                        await event.answer(REGISTER_FIRST, show_alert=True)
                    return  # Halt processing

                # 2. Registered user: check channel subscription
                subscribed = await self._is_subscribed(user.id)
                if not subscribed:
                    name = user.first_name or "Foydalanuvchi"
                    if isinstance(event, Message):
                        await event.answer(
                            CHANNEL_SUBSCRIBE_REQUIRED.format(name=name),
                            reply_markup=channel_subscribe_kb(settings.channel_username),
                            parse_mode="HTML",
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(
                            CHANNEL_SUBSCRIBE_FAIL_ALERT.format(channel=settings.channel_username),
                            show_alert=True,
                        )
                    return  # Halt processing

        return await handler(event, data)
