"""Shared Bot, Dispatcher and FSM storage singletons."""
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis mavjud bo'lsa ishlatamiz, aks holda SQLite-based storage, eng oxiri MemoryStorage
def _build_storage():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            storage = RedisStorage.from_url(redis_url)
            logger.info("✅ FSM storage: RedisStorage")
            return storage
        except Exception as e:
            logger.warning(f"RedisStorage ishlamadi, MemoryStorage ishlatiladi: {e}")

    # Fallback: MemoryStorage
    logger.info("⚠️  FSM storage: MemoryStorage (server qayta ishlaganda holatlar yo'qoladi)")
    return MemoryStorage()


storage = _build_storage()
bot = Bot(token=settings.bot_token)
dp = Dispatcher(storage=storage)
