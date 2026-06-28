"""Controller (handler) layer — wires aiogram events to services + views."""
from aiogram import Dispatcher

from app.container import Container


def register_all(dp: Dispatcher, container: Container) -> None:
    """Register every controller. Order matters: specific before catch-all."""
    from app.controllers import (
        admin, banned_sites, group_protection, menu, private, start, quiz, payments,
    )

    start.register(dp, container)
    admin.register(dp, container)
    banned_sites.register(dp, container)
    quiz.register(dp, container)
    group_protection.register(dp, container)
    menu.register(dp, container)
    payments.register(dp, container)
    private.register(dp, container)

