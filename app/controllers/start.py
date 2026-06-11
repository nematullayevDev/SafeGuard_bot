"""Start, registration, /menu — majburiy kanal obunasi bilan."""
import asyncio
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove,
)

from app.container import Container
from app.controllers.filters import ensure_registered, is_owner
from app.core.bot import bot
from app.core.config import settings
from app.states import Registration
from app.views import keyboards
from app.views.keyboards import (
    channel_subscribe_kb, main_menu, phone_keyboard, persistent_menu_keyboard,
)
from app.views.texts import (
    CHANNEL_SUBSCRIBE_FAIL,
    CHANNEL_SUBSCRIBE_REQUIRED,
    CHANNEL_SUBSCRIBE_SUCCESS,
    PHONE_NOT_UZ,
    REG_REQUIRED,
    WELCOME,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Yordamchi: foydalanuvchi kanalga obuna bo'lganmi?
# ──────────────────────────────────────────────────────────────
async def _is_subscribed(user_id: int) -> bool:
    """True qaytaradi agar foydalanuvchi majburiy kanalga obuna bo'lsa.

    - Kanal sozlanmagan bo'lsa → True (tekshirish o'chirilgan).
    - Tekshirishda xatolik bo'lsa → True (foydalanuvchini bloklamaslik),
      lekin aniq sabab logда ko'rsatiladi (eng keng tarqalgani: bot kanalda admin emas).
    """
    # Avval raqamli ID, bo'lmasa username bo'yicha tekshiramiz
    channel = settings.channel_id if settings.channel_id else settings.channel_username
    if not channel:
        logger.info("Majburiy obuna O'CHIRILGAN — CHANNEL_ID/CHANNEL_USERNAME sozlanmagan.")
        return True
    try:
        member = await bot.get_chat_member(channel, user_id)
        subscribed = member.status not in ("left", "kicked")
        logger.info(
            "Obuna tekshiruvi: user=%s channel=%s status=%s -> obuna=%s",
            user_id, channel, member.status, subscribed,
        )
        return subscribed
    except Exception as e:
        logger.warning(
            "Kanal obuna tekshirishda XATOLIK [channel=%s, user=%s]: %s | "
            "Tekshiring: (1) bot kanalga ADMIN qilib qo'shilgan bo'lsin, "
            "(2) CHANNEL_ID/CHANNEL_USERNAME .env da to'g'ri bo'lsin. "
            "Hozircha foydalanuvchi o'tkazib yuborildi (bloklanmadi).",
            channel, user_id, e,
        )
        return True


async def _send_subscribe_prompt(message: Message) -> None:
    """Kanalga obuna so'rov xabarini yuboradi."""
    name = message.from_user.first_name or "Foydalanuvchi"
    await message.answer(
        CHANNEL_SUBSCRIBE_REQUIRED.format(name=name),
        reply_markup=channel_subscribe_kb(settings.channel_username),
        parse_mode="HTML",
    )


# ──────────────────────────────────────────────────────────────
def register(dp: Dispatcher, c: Container) -> None:

    async def cmd_start_private(message: Message, state: FSMContext):
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"

        parts = (message.text or "").split()
        payload = parts[1] if len(parts) > 1 else ""

        # ── Ro'yxatdan O'TGAN foydalanuvchi ──────────────────
        if c.users.is_registered(uid):
            # Kanalga obuna tekshiruvi
            if not await _is_subscribed(uid):
                await _send_subscribe_prompt(message)
                return

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
                    parse_mode="HTML",
                )
                return

            await message.answer(
                WELCOME.format(name=name),
                reply_markup=main_menu(is_owner(message)),
                parse_mode="HTML",
            )
            return

        # ── Ro'yxatdan O'TMAGAN foydalanuvchi ────────────────
        await state.update_data(payload=payload)
        await message.answer(
            REG_REQUIRED.format(name=name),
            reply_markup=phone_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(Registration.waiting_phone)

    # ──────────────────────────────────────────────────────────
    # Telefon raqami keldi → ro'yxatdan o'tkazish
    # ──────────────────────────────────────────────────────────
    async def handle_phone(message: Message, state: FSMContext):
        contact = message.contact
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"
        username = message.from_user.username or ""
        phone = contact.phone_number

        # +998 tekshiruvi — faqat O'zbekiston raqamlari
        normalized = phone.lstrip("+").strip()
        if not normalized.startswith("998"):
            await message.answer(
                PHONE_NOT_UZ.format(phone=f"+{normalized}"),
                reply_markup=phone_keyboard(),
                parse_mode="HTML",
            )
            return

        c.users.save(uid, name, username, phone)

        state_data = await state.get_data()
        payload = state_data.get("payload", "")
        await state.clear()

        # Adminga yangi foydalanuvchi haqida xabar
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
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        await asyncio.sleep(0.5)

        # ── Kanalga obuna tekshiruvi (ro'yxatdan keyin) ──────
        if not await _is_subscribed(uid):
            await message.answer(
                CHANNEL_SUBSCRIBE_REQUIRED.format(name=name),
                reply_markup=channel_subscribe_kb(settings.channel_username),
                parse_mode="HTML",
            )
            return

        # Obuna tasdiqlangan → menyuga o'tish
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
                parse_mode="HTML",
            )
        else:
            await message.answer(
                WELCOME.format(name=name),
                reply_markup=main_menu(is_owner(message)),
                parse_mode="HTML",
            )

    # ──────────────────────────────────────────────────────────
    # «✅ Tekshirish» tugmasi bosildi
    # ──────────────────────────────────────────────────────────
    async def handle_check_subscription(call: CallbackQuery):
        uid = call.from_user.id
        name = call.from_user.first_name or "Foydalanuvchi"

        if await _is_subscribed(uid):
            # Obuna tasdiqlandi ✅
            await call.message.edit_text(
                CHANNEL_SUBSCRIBE_SUCCESS,
                parse_mode="HTML",
            )
            await asyncio.sleep(0.5)
            # Menyuga yo'naltirish
            await call.message.answer(
                WELCOME.format(name=name),
                reply_markup=main_menu(is_owner(call)),
                parse_mode="HTML",
            )
        else:
            # Hali obuna bo'lmagan ❌
            await call.answer(
                CHANNEL_SUBSCRIBE_FAIL.format(channel=settings.channel_username),
                show_alert=True,
            )

    async def handle_phone_wrong(message: Message):
        await message.answer(
            "⚠️ Iltimos, quyidagi tugmani bosib raqamingizni ulashing 👇",
            reply_markup=phone_keyboard(),
        )

    async def cmd_menu(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"

        # Kanal tekshiruvi /menu buyrug'ida ham
        if not await _is_subscribed(uid):
            await _send_subscribe_prompt(message)
            return

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
            parse_mode="HTML",
            reply_markup=kb,
        )

    # ── Handler'larni ro'yxatdan o'tkazish ───────────────────
    dp.message.register(cmd_start_private, Command("start"), F.chat.type == "private")
    dp.message.register(handle_phone, Registration.waiting_phone, F.contact)
    dp.message.register(handle_phone_wrong, Registration.waiting_phone)
    dp.message.register(cmd_menu, Command("menu"), F.chat.type == "private")
    dp.message.register(
        cmd_start_group, Command("start"),
        F.chat.type.in_({"group", "supergroup"}),
    )
    dp.callback_query.register(handle_check_subscription, F.data == "check_subscription")
