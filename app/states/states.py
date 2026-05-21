"""FSM states."""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_phone = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


class AddSiteState(StatesGroup):
    choosing_platform = State()
    waiting_site_name = State()
