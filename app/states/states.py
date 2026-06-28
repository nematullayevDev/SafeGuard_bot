"""FSM states."""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_lang = State()
    waiting_phone = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


class AddSiteState(StatesGroup):
    choosing_platform = State()
    waiting_site_name = State()


class QuizState(StatesGroup):
    answering = State()


class AssistantState(StatesGroup):
    chatting = State()


class GroupSettingsState(StatesGroup):
    waiting_keywords = State()
    waiting_whitelist = State()


class AdminState(StatesGroup):
    waiting_premium_user = State()


