"""Start, registration, /menu."""
import asyncio
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove,
)

from app.container import Container
from app.controllers.filters import ensure_registered, is_owner
from app.core.bot import bot
from app.core.config import settings
from app.states import Registration
from app.views import keyboards
from app.views.keyboards import main_menu, phone_keyboard, persistent_menu_keyboard
from app.views.texts import REG_REQUIRED, WELCOME

logger = logging.getLogger(__name__)


def register(dp: Dispatcher, c: Container) -> None:
    async def cmd_start_private(message: Message, state: FSMContext):
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"

        parts = (message.text or "").split()
        payload = parts[1] if len(parts) > 1 else ""

        if c.users.is_registered(uid):
            if payload == "quiz":
                status = c.users.get_quiz_status(uid)
                quiz_passed = status.get("passed", False)
                await message.answer(
                    "🛡️ <b>SafeGuard Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Ushbu interaktiv test kiberxavfsizlik sohasidagi asosiy tushunchalarni tekshirish "
                    "va oshirish uchun yaratilgan.\n\n"
                    "📝 Test <b>5 ta professional savoldan</b> iborat bo'lib, o'tish uchun kamida <b>4 ta to'g'ri javob</b> topishingiz kerak.\n\n"
                    "🎉 Testdan muvaffaqiyatli o'tsangiz, profilingiz yonida maxsus **`🛡️`** nishoni paydo bo'ladi!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=keyboards.quiz_main_menu(quiz_passed),
                    parse_mode="HTML"
                )
                return

            await message.answer(
                WELCOME.format(name=name),
                reply_markup=main_menu(is_owner(message)),
                parse_mode="HTML",
            )
            return

        await state.update_data(payload=payload)
        await message.answer(
            REG_REQUIRED.format(name=name),
            reply_markup=phone_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(Registration.waiting_phone)

    async def handle_phone(message: Message, state: FSMContext):
        contact = message.contact
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"
        username = message.from_user.username or ""
        phone = contact.phone_number

        c.users.save(uid, name, username, phone)
        
        state_data = await state.get_data()
        payload = state_data.get("payload", "")
        await state.clear()

        if settings.admin_id:
            try:
                uname = f"@{username}" if username else "Yo'q"
                await bot.send_message(
                    settings.admin_id,
                    "🆕 <b>Yangi foydalanuvchi ro'yxatdan o'tdi!</b>\n\n"
                    f"👤 Ism: {name}\n"
                    f"🔗 Username: {uname}\n"
                    f"📱 Telefon: {phone}\n"
                    f"🆔 ID: {uid}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Adminga xabar: %s", e)

        await message.answer(
            "✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
            "Endi botdan to'liq foydalanishingiz mumkin.",
            reply_markup=ReplyKeyboardRemove(), parse_mode="HTML",
        )
        await asyncio.sleep(0.5)

        if payload == "quiz":
            status = c.users.get_quiz_status(uid)
            quiz_passed = status.get("passed", False)
            await message.answer(
                "🛡️ <b>SafeGuard Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Ushbu interaktiv test kiberxavfsizlik sohasidagi asosiy tushunchalarni tekshirish "
                "va oshirish uchun yaratilgan.\n\n"
                "📝 Test <b>5 ta professional savoldan</b> iborat bo'lib, o'tish uchun kamida <b>4 ta to'g'ri javob</b> topishingiz kerak.\n\n"
                "🎉 Testdan muvaffaqiyatli o'tsangiz, profilingiz yonida maxsus **`🛡️`** nishoni paydo bo'ladi!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=keyboards.quiz_main_menu(quiz_passed),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                WELCOME.format(name=name),
                reply_markup=main_menu(is_owner(message)),
                parse_mode="HTML",
            )


    async def handle_phone_wrong(message: Message):
        await message.answer(
            "⚠️ Iltimos, quyidagi tugmani bosib raqamingizni ulashing 👇",
            reply_markup=phone_keyboard(),
        )

    async def cmd_menu(message: Message):
        if not await ensure_registered(message, c):
            return
        name = message.from_user.first_name or "Foydalanuvchi"
        await message.answer(
            WELCOME.format(name=name),
            reply_markup=main_menu(is_owner(message)),
            parse_mode="HTML",
        )

    async def cmd_start_group(message: Message):
        info = await bot.get_me()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🤖 Shaxsiy botni ochish",
                url=f"https://t.me/{info.username}?start=from_group",
            )]
        ])
        await message.reply(
            "🛡 <b>SafeGuard</b> bu guruhni himoya qilmoqda!\n\n"
            "Botdan shaxsiy foydalanish uchun quyidagi tugmani bosing 👇",
            parse_mode="HTML", reply_markup=kb,
        )

    dp.message.register(cmd_start_private, Command("start"), F.chat.type == "private")
    dp.message.register(handle_phone, Registration.waiting_phone, F.contact)
    dp.message.register(handle_phone_wrong, Registration.waiting_phone)
    dp.message.register(cmd_menu, Command("menu"), F.chat.type == "private")
    dp.message.register(cmd_start_group, Command("start"),
                        F.chat.type.in_({"group", "supergroup"}))
