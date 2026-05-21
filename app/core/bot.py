"""Shared Bot, Dispatcher and FSM storage singletons."""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings

storage = MemoryStorage()
bot = Bot(token=settings.bot_token)
dp = Dispatcher(storage=storage)
