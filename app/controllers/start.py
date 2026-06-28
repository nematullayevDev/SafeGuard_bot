"""Start, registration, /menu — majburiy kanal obunasi bilan."""
import asyncio
import logging
import time

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
    channel_subscribe_kb, main_menu, phone_keyboard,
)
from app.views.texts import get_text

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Yordamchi: foydalanuvchi kanalga obuna bo'lganmi?
# ──────────────────────────────────────────────────────────────
async def _is_subscribed(user_id: int) -> bool:
    """True qaytaradi agar foydalanuvchi majburiy kanalga obuna bo'lsa."""
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
            "Hozircha foydalanuvchi o'tkazib yuborildi (bloklanmadi).",
            channel, user_id, e,
        )
        return True


async def _send_subscribe_prompt(message: Message, lang: str = "uz") -> None:
    """Kanalga obuna so'rov xabarini yuboradi."""
    name = message.from_user.first_name or "Foydalanuvchi"
    await message.answer(
        get_text("channel_subscribe_required", lang).format(name=name),
        reply_markup=channel_subscribe_kb(settings.channel_username, lang),
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
            lang = c.users.get_language(uid)
            # Kanalga obuna tekshiruvi
            if not await _is_subscribed(uid):
                await _send_subscribe_prompt(message, lang)
                return

            if payload == "quiz":
                status = c.users.get_quiz_status(uid)
                quiz_passed = status.get("passed", False)
                
                quiz_title = {
                    "uz": "🛡️ <b>SafeGuard Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                          "Ushbu interaktiv test kiberxavfsizlik sohasidagi asosiy tushunchalarni tekshirish "
                          "va oshirish uchun yaratilgan.\n\n"
                          "📝 Test <b>5 ta professional savoldan</b> iborat bo'lib, o'tish uchun kamida <b>4 ta to'g'ri javob</b> topishingiz kerak.\n\n"
                          "🎉 Testdan muvaffaqiyatli o'tsangiz, profilingiz yonida maxsus **`🛡️`** nishoni paydo bo'ladi!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "uz_cyr": "🛡️ <b>SafeGuard Кибер-Саводхонлик Викторинаси</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                              "Ушбу интерактив тест киберхавфсизлик соҳасидаги асосий тушунчаларни текшириш "
                              "ва ошириш учун яратилган.\n\n"
                              "📝 Тест <b>5 та профессионал саволдан</b> иборат бўлиб, ўтиш учун камида <b>4 та тўғри жавоб</b> топишингиз керак.\n\n"
                              "🎉 Тестдан муваффақиятли ўтсангиз, профилингиз ёнида махсус **`🛡️`** нишони пайдо бўлади!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "ru": "🛡️ <b>Викторина Киберграмотности SafeGuard</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                          "Этот интерактивный тест создан для проверки и повышения ваших базовых знаний в области кибербезопасности.\n\n"
                          "📝 Тест состоит из <b>5 профессиональных вопросов</b>. Для успешного прохождения нужно правильно ответить минимум на <b>4 вопроса</b>.\n\n"
                          "🎉 После успешного прохождения теста в вашем профиле и списке участников появится специальный знак **`🛡️`**!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "en": "🛡️ <b>SafeGuard Cyber-Literacy Quiz</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                          "This interactive test is designed to verify and improve your basic cybersecurity knowledge.\n\n"
                          "📝 The quiz consists of <b>5 professional questions</b>. You must answer at least <b>4 questions</b> correctly to pass.\n\n"
                          "🎉 After passing the quiz, a special **`🛡️`** badge will appear next to your profile in the users list!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                }.get(lang, "")
                
                await message.answer(
                    quiz_title,
                    reply_markup=keyboards.quiz_main_menu(quiz_passed, lang),
                    parse_mode="HTML",
                )
                return

            if payload == "help_group":
                guide_text = {
                    "uz": (
                        "📖 <b>SafeGuard — Guruh Himoyasi Qo'llanmasi</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "Guruhingiz kiberxavfsizligini ta'minlash uchun quyidagi amallarni bajaring:\n\n"
                        "1️⃣ <b>Botni guruhga qo'shing</b> va unga <b>Admin (Administrator)</b> huquqini bering.\n"
                        "2️⃣ Havolalar, fayllar va QR-kodlarni tekshirish avtomatik rejimda ishga tushadi.\n"
                        "3️⃣ Guruh sozlamalarini boshqarish uchun guruh ichida <b>/settings</b> buyrug'ini yuboring.\n"
                        "4️⃣ Guruh muloqot tilini o'zgartirish uchun guruh ichida <b>/lang</b> buyrug'ini bering.\n\n"
                        "⚡ <b>Taqiqlangan kalit so'zlar (Keywords):</b>\n"
                        "Guruh a'zolari yozishi taqiqlangan so'zlar ro'yxatini sozlang. Kimdir shu so'zlarni yozsa, xabari o'chiriladi va ogohlantirish beriladi.\n\n"
                        "🔗 <b>Oq ro'yxat (Whitelist):</b>\n"
                        "Siz ishonadigan saytlar (masalan: <code>google.com</code>, <code>my.gov.uz</code>) manzillarini kiriting. Bot ularni virus tahlilidan o'tkazmaydi.\n\n"
                        "⚠️ <b>Ogohlantirish limiti (Warn Limit):</b>\n"
                        "Foydalanuvchilar qonunbuzarlik qilganda necha marta ogohlantirish olgach guruhdan chiqarilishini belgilang (Odatiy: 3 marta)."
                    ),
                    "uz_cyr": (
                        "📖 <b>SafeGuard — Гуруҳ Ҳимояси Қўлланмаси</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "Гуруҳингиз киберхавфсизлигини таъминлаш учун қуйидаги амалларни бажаринг:\n\n"
                        "1️⃣ <b>Ботни гуруҳга қўшинг</b> ва унга <b>Админ (Администратор)</b> ҳуқуқини беринг.\n"
                        "2️⃣ Ҳаволалар, файллар ва QR-кодларни текшириш автоматик режимда ишга тушади.\n"
                        "3️⃣ Гуруҳ созламаларини бошқариш учун гуруҳ ичида <b>/settings</b> буйруғини юборинг.\n"
                        "4️⃣ Гуруҳ мулоқот тилини ўзгартириш учун гуруҳ ичида <b>/lang</b> буйруғини беринг.\n\n"
                        "⚡ <b>Тақиқланган калит сўзлар (Keywords):</b>\n"
                        "Гуруҳ аъзолари ёзиши тақиқланган сўзлар рўйхатини созланг. Кимдир шу сўзларни ёзса, хабари ўчирилади ва огоҳлантириш берилади.\n\n"
                        "🔗 <b>Оқ рўйхат (Whitelist):</b>\n"
                        "Сиз ишонадиган сайтлар (маслан: <code>google.com</code>, <code>my.gov.uz</code>) манзилларини киритинг. Бот уларни вирус таҳлилидан ўтказмайди.\n\n"
                        "⚠️ <b>Огоҳлантириш лимити (Warn Limit):</b>\n"
                        "Фойдаланувчилар қонунбузарлик қилганда неча марта огоҳлантириш олгач гуруҳдан чиқарилишини белгиланг (Одатий: 3 марта)."
                    ),
                    "ru": (
                        "📖 <b>SafeGuard — Инструкция по защите групп</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "Для обеспечения кибербезопасности вашей группы выполните следующие шаги:\n\n"
                        "1️⃣ <b>Добавьте бота в группу</b> и предоставьте ему права <b>Администратора</b>.\n"
                        "2️⃣ Проверка ссылок, файлов и QR-кодов запустится автоматически.\n"
                        "3️⃣ Для настройки защиты отправьте команду <b>/settings</b> внутри группы.\n"
                        "4️⃣ Для изменения языка группы отправьте команду <b>/lang</b> внутри группы.\n\n"
                        "⚡ <b>Запрещенные ключевые слова (Keywords):</b>\n"
                        "Настройте список слов, которые запрещено писать участникам. При их обнаружении сообщение удаляется, а пользователю выдается предупреждение.\n\n"
                        "🔗 <b>Белый список (Whitelist):</b>\n"
                        "Добавьте доверенные домены (например: <code>google.com</code>, <code>my.gov.uz</code>). Бот не будет блокировать их при отправке.\n\n"
                        "⚠️ <b>Лимит предупреждений (Warn Limit):</b>\n"
                        "Укажите, после скольких предупреждений нарушитель будет заблокирован в группе (По умолчанию: 3)."
                    ),
                    "en": (
                        "📖 <b>SafeGuard — Group Protection Guide</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "To secure your group, follow these simple steps:\n\n"
                        "1️⃣ <b>Add the bot to your group</b> and grant it <b>Admin privileges</b>.\n"
                        "2️⃣ File, link, and QR-code scans will start running automatically.\n"
                        "3️⃣ Send the <b>/settings</b> command inside the group to customize protection.\n"
                        "4️⃣ Send the <b>/lang</b> command inside the group to change communication language.\n\n"
                        "⚡ <b>Banned Keywords:</b>\n"
                        "Configure forbidden words. Messages containing these will be deleted and the sender warned.\n\n"
                        "🔗 <b>Whitelisted Domains:</b>\n"
                        "Add trusted domains (e.g. <code>google.com</code>, <code>my.gov.uz</code>). The bot will bypass scans for these links.\n\n"
                        "⚠️ <b>Warnings Limit:</b>\n"
                        "Configure the maximum warnings allowed before a member is banned (Default: 3)."
                    )
                }.get(lang, "")
                
                await message.answer(
                    guide_text,
                    reply_markup=keyboards.go_start_kb(lang),
                    parse_mode="HTML",
                )
                return

            await message.answer(
                get_text("welcome", lang).format(name=name),
                reply_markup=keyboards.main_reply_menu(lang),
                parse_mode="HTML",
            )
            
            protect_title = {
                "uz": "🛡️ <b>SafeGuard Kiber-Himoya Tizimi</b>\n\nUshbu panel orqali kiberxavfsizlik modullarini boshqarishingiz, kiber-viktorinada qatnashishingiz va AI yordamchidan maslahat olishingiz mumkin.\n\nQuyidagi tugmalardan birini tanlang:",
                "uz_cyr": "🛡️ <b>SafeGuard Кибер-Ҳимоя Тизими</b>\n\nУшбу панел орқали киберхавфсизлик модулларини бошқаришингиз, кибер-викторинада қатнашишингиз ва AI ёрдамчидан маслаҳат олишингиз мумкин.\n\nҚуйидаги тугмалардан бирини танланг:",
                "ru": "🛡️ <b>Система Киберзащиты SafeGuard</b>\n\nЧерез эту панель вы можете управлять модулями кибербезопасности, участвовать в кибер-викторине и консультироваться с ИИ-помощником.\n\nВыберите одну из кнопок ниже:",
                "en": "🛡️ <b>SafeGuard Cyber-Protection System</b>\n\nThrough this panel you can manage cybersecurity modules, participate in the cyber-quiz, and consult with the AI assistant.\n\nSelect one of the buttons below:"
            }.get(lang, "")
            
            await message.answer(
                protect_title,
                reply_markup=keyboards.protection_panel_kb(lang),
                parse_mode="HTML",
            )
            return

        # ── Ro'yxatdan O'TMAGAN foydalanuvchi ────────────────
        await state.update_data(payload=payload)
        await message.answer(
            "🌐 Iltimos, muloqot tilini tanlang:\n"
            "🌐 Пожалуйста, выберите язык общения:\n"
            "🌐 Please select your communication language:",
            reply_markup=keyboards.language_selection_kb()
        )
        await state.set_state(Registration.waiting_lang)

    # ──────────────────────────────────────────────────────────
    # Til tanlandi -> Telefon raqam so'rash
    # ──────────────────────────────────────────────────────────
    async def handle_set_lang_callback(call: CallbackQuery, state: FSMContext):
        lang = call.data[8:]  # setlang_ length is 8
        uid = call.from_user.id
        name = call.from_user.first_name or "Foydalanuvchi"
        
        current_state = await state.get_state()
        if current_state == Registration.waiting_lang:
            await state.update_data(lang=lang)
            try:
                await call.message.delete()
            except Exception:
                pass
            await call.message.answer(
                get_text("reg_required", lang).format(name=name),
                reply_markup=phone_keyboard(lang),
                parse_mode="HTML"
            )
            await state.set_state(Registration.waiting_phone)
        else:
            # Sozlamalar menyusi orqali til o'zgartirildi
            c.users.set_language(uid, lang)
            confirm_text = {
                "uz": "✅ Muloqot tili o'zgartirildi!",
                "uz_cyr": "✅ Мулоқот тили ўзгартирилди!",
                "ru": "✅ Язык общения изменен!",
                "en": "✅ Communication language changed!"
            }.get(lang, "✅")
            await call.answer(confirm_text)
            
            await call.message.edit_text(
                get_text("welcome", lang).format(name=name),
                reply_markup=main_menu(is_owner(call), lang),
                parse_mode="HTML"
            )
        await call.answer()

    # ──────────────────────────────────────────────────────────
    # Telefon raqami keldi → ro'yxatdan o'tkazish
    # ──────────────────────────────────────────────────────────
    async def handle_phone(message: Message, state: FSMContext):
        contact = message.contact
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"
        username = message.from_user.username or ""
        phone = contact.phone_number

        state_data = await state.get_data()
        lang = state_data.get("lang", "uz")
        payload = state_data.get("payload", "")

        # +998 tekshiruvi — faqat O'zbekiston raqamlari
        normalized = phone.lstrip("+").strip()
        if not normalized.startswith("998"):
            await message.answer(
                get_text("phone_not_uz", lang).format(phone=f"+{normalized}"),
                reply_markup=phone_keyboard(lang),
                parse_mode="HTML",
            )
            return

        c.users.save(uid, name, username, phone, lang)
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
                    f"🌐 Til: {lang}\n"
                    f"🆔 ID: {uid}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Adminga xabar: %s", e)

        # ── Kanalga obuna tekshiruvi (ro'yxatdan keyin) ──────
        is_sub = await _is_subscribed(uid)
        if not is_sub:
            reg_ok = {
                "uz": "✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\nBotdan foydalanishni boshlash uchun rasmiy kanalimizga obuna bo'lishingiz lozim 👇",
                "uz_cyr": "✅ <b>Рўйхатдан муваффақиятли ўтдингиз!</b>\n\nБотдан фойдаланишни бошлаш учун расмий каналимизга обуна бўлишингиз лозим 👇",
                "ru": "✅ <b>Вы успешно зарегистрировались!</b>\n\nДля начала работы с ботом необходимо подписаться на наш официальный канал 👇",
                "en": "✅ <b>You have successfully registered!</b>\n\nTo start using the bot, you must subscribe to our official channel 👇"
            }.get(lang, "")
            await message.answer(
                reg_ok,
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML",
            )
            await asyncio.sleep(0.5)
            await message.answer(
                get_text("channel_subscribe_required", lang).format(name=name),
                reply_markup=channel_subscribe_kb(settings.channel_username, lang),
                parse_mode="HTML",
            )
            return

        success_msg = {
            "uz": "✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\nEndi botdan to'liq foydalanishingiz mumkin.",
            "uz_cyr": "✅ <b>Рўйхатдан муваффақиятли ўтдингиз!</b>\n\nЭнди ботдан тўлиқ фойдаланишингиз мумкин.",
            "ru": "✅ <b>Вы успешно зарегистрировались!</b>\n\nТеперь вы можете полноценно использовать бота.",
            "en": "✅ <b>You have successfully registered!</b>\n\nNow you can fully use the bot."
        }.get(lang, "")
        
        await message.answer(
            success_msg,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        await asyncio.sleep(0.5)

        # Obuna tasdiqlangan → menyuga o'tish
        if payload == "quiz":
            status = c.users.get_quiz_status(uid)
            quiz_passed = status.get("passed", False)
            
            quiz_title = {
                "uz": "🛡️ <b>SafeGuard Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      "Ushbu interaktiv test kiberxavfsizlik sohasidagi asosiy tushunchalarni tekshirish "
                      "va oshirish uchun yaratilgan.\n\n"
                      "📝 Test <b>5 ta professional savoldan</b> iborat bo'lib, o'tish uchun kamida <b>4 ta to'g'ri javob</b> topishingiz kerak.\n\n"
                      "🎉 Testdan muvaffaqiyatli o'tsangiz, profilingiz yonida maxsus **`🛡️`** nishoni paydo bo'ladi!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "uz_cyr": "🛡️ <b>SafeGuard Кибер-Саводхонлик Викторинаси</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                          "Ушбу интерактив тест киберхавфсизлик соҳасидаги асосий тушунчаларни текшириш "
                          "ва ошириш учун яратилган.\n\n"
                          "📝 Тест <b>5 та профессионал саволдан</b> иборат бўлиб, ўтиш учун камида <b>4 та тўғри жавоб</b> топишингиз керак.\n\n"
                          "🎉 Тестдан муваффақиятли ўтсангиз, профилингиз ёнида махсус **`🛡️`** нишони пайдо бўлади!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "ru": "🛡️ <b>Викторина Киберграмотности SafeGuard</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      "Этот интерактивный тест создан для проверки и повышения ваших базовых знаний в области кибербезопасности.\n\n"
                      "📝 Тест состоит из <b>5 профессиональных вопросов</b>. Для успешного прохождения нужно правильно ответить минимум на <b>4 вопроса</b>.\n\n"
                      "🎉 После успешного прохождения теста в вашем профиле и списке участников появится специальный знак **`🛡️`**!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "en": "🛡️ <b>SafeGuard Cyber-Literacy Quiz</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      "This interactive test is designed to verify and improve your basic cybersecurity knowledge.\n\n"
                      "📝 The quiz consists of <b>5 professional questions</b>. You must answer at least <b>4 questions</b> correctly to pass.\n\n"
                      "🎉 After passing the quiz, a special **`🛡️`** badge will appear next to your profile in the users list!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            }.get(lang, "")
            
            await message.answer(
                quiz_title,
                reply_markup=keyboards.quiz_main_menu(quiz_passed, lang),
                parse_mode="HTML",
            )
        elif payload == "help_group":
            guide_text = {
                "uz": (
                    "📖 <b>SafeGuard — Guruh Himoyasi Qo'llanmasi</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Guruhingiz kiberxavfsizligini ta'minlash uchun quyidagi amallarni bajaring:\n\n"
                    "1️⃣ <b>Botni guruhga qo'shing</b> va unga <b>Admin (Administrator)</b> huquqini bering.\n"
                    "2️⃣ Havolalar, fayllar va QR-kodlarni tekshirish avtomatik rejimda ishga tushadi.\n"
                    "3️⃣ Guruh sozlamalarini boshqarish uchun guruh ichida <b>/settings</b> buyrug'ini yuboring.\n"
                    "4️⃣ Guruh muloqot tilini o'zgartirish uchun guruh ichida <b>/lang</b> buyrug'ini bering.\n\n"
                    "⚡ <b>Taqiqlangan kalit so'zlar (Keywords):</b>\n"
                    "Guruh a'zolari yozishi taqiqlangan so'zlar ro'yxatini sozlang. Kimdir shu so'zlarni yozsa, xabari o'chiriladi va ogohlantirish beriladi.\n\n"
                    "🔗 <b>Oq ro'yxat (Whitelist):</b>\n"
                    "Siz ishonadigan saytlar (masalan: <code>google.com</code>, <code>my.gov.uz</code>) manzillarini kiriting. Bot ularni virus tahlilidan o'tkazmaydi.\n\n"
                    "⚠️ <b>Ogohlantirish limiti (Warn Limit):</b>\n"
                    "Foydalanuvchilar qonunbuzarlik qilganda necha marta ogohlantirish olgach guruhdan chiqarilishini belgilang (Odatiy: 3 marta)."
                ),
                "uz_cyr": (
                    "📖 <b>SafeGuard — Гуруҳ Ҳимояси Қўлланмаси</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Гуруҳингиз киберхавфсизлигини таъминлаш учун қуйидаги амалларни бажаринг:\n\n"
                    "1️⃣ <b>Ботни гуруҳга қўшинг</b> ва унга <b>Админ (Администратор)</b> ҳуқуқини беринг.\n"
                    "2️⃣ Ҳаволалар, файллар ва QR-кодларни текшириш автоматик режимда ишга тушади.\n"
                    "3️⃣ Гуруҳ созламаларини бошқариш учун гуруҳ ичида <b>/settings</b> буйруғини юборинг.\n"
                    "4️⃣ Гуруҳ мулоқот тилини ўзгартириш uchun гуруҳ ичида <b>/lang</b> буйруғини беринг.\n\n"
                    "⚡ <b>Тақиқланган калит сўзлар (Keywords):</b>\n"
                    "Гуруҳ аъзолари ёзиши тақиқланган сўзлар рўйхатини созланг. Кимдир шу сўзларни ёзса, хабари ўчирилади ва огоҳлантириш берилади.\n\n"
                    "🔗 <b>Оқ рўйхат (Whitelist):</b>\n"
                    "Сиз ишонадиган сайтлар (маслан: <code>google.com</code>, <code>my.gov.uz</code>) манзилларини киритинг. Бот уларни вирус таҳлилидан ўтказмайди.\n\n"
                    "⚠️ <b>Огоҳлантириш лимити (Warn Limit):</b>\n"
                    "Фойдаланувчилар қонунбузарлик қилганда неча марта огоҳлантириш олгач гуруҳдан чиқарилишини белгиланг (Одатий: 3 марта)."
                ),
                "ru": (
                    "📖 <b>SafeGuard — Инструкция по защите групп</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Для обеспечения кибербезопасности вашей группы выполните следующие шаги:\n\n"
                    "1️⃣ <b>Добавьте бота в группу</b> и предоставьте ему права <b>Администратора</b>.\n"
                    "2️⃣ Проверка ссылок, файлов и QR-кодов запустится автоматически.\n"
                    "3️⃣ Для настройки защиты отправьте команду <b>/settings</b> внутри группы.\n"
                    "4️⃣ Для изменения языка группы отправьте команду <b>/lang</b> внутри группы.\n\n"
                    "⚡ <b>Запрещенные ключевые слова (Keywords):</b>\n"
                    "Настройте список слов, которые запрещено писать участникам. При их обнаружении сообщение удаляется, а пользователю выдается предупреждение.\n\n"
                    "🔗 <b>Белый список (Whitelist):</b>\n"
                    "Добавьте доверенные домены (например: <code>google.com</code>, <code>my.gov.uz</code>). Бот не будет блокировать их при отправке.\n\n"
                    "⚠️ <b>Лимит предупреждений (Warn Limit):</b>\n"
                    "Укажите, после скольких предупреждений нарушитель будет заблокирован в группе (По умолчанию: 3)."
                ),
                "en": (
                    "📖 <b>SafeGuard — Group Protection Guide</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "To secure your group, follow these simple steps:\n\n"
                    "1️⃣ <b>Add the bot to your group</b> and grant it <b>Admin privileges</b>.\n"
                    "2️⃣ File, link, and QR-code scans will start running automatically.\n"
                    "3️⃣ Send the <b>/settings</b> command inside the group to customize protection.\n"
                    "4️⃣ Send the <b>/lang</b> command inside the group to change communication language.\n\n"
                    "⚡ <b>Banned Keywords:</b>\n"
                    "Configure forbidden words. Messages containing these will be deleted and the sender warned.\n\n"
                    "🔗 <b>Whitelisted Domains:</b>\n"
                    "Add trusted domains (e.g. <code>google.com</code>, <code>my.gov.uz</code>). The bot will bypass scans for these links.\n\n"
                    "⚠️ <b>Warnings Limit:</b>\n"
                    "Configure the maximum warnings allowed before a member is banned (Default: 3)."
                )
            }.get(lang, "")
            await message.answer(
                guide_text,
                reply_markup=keyboards.go_start_kb(lang),
                parse_mode="HTML",
            )
        else:
            await message.answer(
                get_text("welcome", lang).format(name=name),
                reply_markup=keyboards.main_reply_menu(lang),
                parse_mode="HTML",
            )
            
            protect_title = {
                "uz": "🛡️ <b>SafeGuard Kiber-Himoya Tizimi</b>\n\nUshbu panel orqali kiberxavfsizlik modullarini boshqarishingiz, kiber-viktorinada qatnashishingiz va AI yordamchidan maslahat olishingiz mumkin.\n\nQuyidagi tugmalardan birini tanlang:",
                "uz_cyr": "🛡️ <b>SafeGuard Кибер-Ҳимоя Тизими</b>\n\nУшбу панел орқали киберхавфсизлик модулларини бошқаришингиз, кибер-викторинада қатнашишингиз ва AI ёрдамчидан маслаҳат олишингиз мумкин.\n\nҚуйидаги тугмалардан бирини танланг:",
                "ru": "🛡️ <b>Система Киберзащиты SafeGuard</b>\n\nЧерез эту панель вы можете управлять модулями кибербезопасности, участвовать в кибер-викторине и консультироваться с ИИ-помощником.\n\nВыберите одну из кнопок ниже:",
                "en": "🛡️ <b>SafeGuard Cyber-Protection System</b>\n\nThrough this panel you can manage cybersecurity modules, participate in the cyber-quiz, and consult with the AI assistant.\n\nSelect one of the buttons below:"
            }.get(lang, "")
            
            await message.answer(
                protect_title,
                reply_markup=keyboards.protection_panel_kb(lang),
                parse_mode="HTML",
            )

    # ──────────────────────────────────────────────────────────
    # «✅ Tekshirish» tugmasi bosildi
    # ──────────────────────────────────────────────────────────
    async def handle_check_subscription(call: CallbackQuery):
        uid = call.from_user.id
        name = call.from_user.first_name or "Foydalanuvchi"
        lang = c.users.get_language(uid)

        if await _is_subscribed(uid):
            # Obuna tasdiqlandi ✅
            SubscriptionMiddleware = c.rate_limiter # dummy reference to avoid circular import issues if middleware is changed
            import time
            from app.core.middlewares import SubscriptionMiddleware
            SubscriptionMiddleware.cache[uid] = (True, time.time() + SubscriptionMiddleware.cache_ttl)

            await call.message.edit_text(
                get_text("channel_subscribe_success", lang),
                parse_mode="HTML",
            )
            await asyncio.sleep(0.5)
            # Menyuga yo'naltirish
            await call.message.answer(
                get_text("welcome", lang).format(name=name),
                reply_markup=main_menu(is_owner(call), lang),
                parse_mode="HTML",
            )
        else:
            # Hali obuna bo'lmagan ❌
            from app.core.middlewares import SubscriptionMiddleware
            SubscriptionMiddleware.cache.pop(uid, None)

            await call.answer(
                get_text("channel_subscribe_fail_alert", lang).format(channel=settings.channel_username),
                show_alert=True,
            )

    async def handle_phone_wrong(message: Message, state: FSMContext):
        state_data = await state.get_data()
        lang = state_data.get("lang", "uz")
        text = {
            "uz": "⚠️ Iltimos, quyidagi tugmani bosib raqamingizni ulashing 👇",
            "uz_cyr": "⚠️ Илтимос, қуйидаги тугмани босиб рақамингизни улашинг 👇",
            "ru": "⚠️ Пожалуйста, нажмите кнопку ниже, чтобы поделиться контактом 👇",
            "en": "⚠️ Please press the button below to share your contact 👇"
        }.get(lang, "⚠️")
        await message.answer(
            text,
            reply_markup=phone_keyboard(lang),
        )

    async def cmd_menu(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        name = message.from_user.first_name or "Foydalanuvchi"
        lang = c.users.get_language(uid)

        # Kanal tekshiruvi /menu buyrug'ida ham
        if not await _is_subscribed(uid):
            await _send_subscribe_prompt(message, lang)
            return

        await message.answer(
            get_text("welcome", lang).format(name=name),
            reply_markup=main_menu(is_owner(message), lang),
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

    async def cmd_lang(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        text = {
            "uz": "🌐 Yangi muloqot tilini tanlang:",
            "uz_cyr": "🌐 Янги мулоқот тилини танланг:",
            "ru": "🌐 Выберите новый язык общения:",
            "en": "🌐 Select new communication language:"
        }.get(lang, "🌐")
        await message.answer(
            text,
            reply_markup=keyboards.language_selection_kb()
        )

    async def handle_change_language_private(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        text = {
            "uz": "🌐 Yangi muloqot tilini tanlang:",
            "uz_cyr": "🌐 Янги мулоқот тилини танланг:",
            "ru": "🌐 Выберите новый язык общения:",
            "en": "🌐 Select new communication language:"
        }.get(lang, "🌐")
        await call.message.edit_text(
            text,
            reply_markup=keyboards.language_selection_kb()
        )
        await call.answer()

    # ── Handler'larni ro'yxatdan o'tkazish ───────────────────
    dp.message.register(cmd_start_private, Command("start"), F.chat.type == "private")
    dp.callback_query.register(handle_set_lang_callback, F.data.startswith("setlang_"))
    dp.message.register(handle_phone, Registration.waiting_phone, F.contact)
    dp.message.register(handle_phone_wrong, Registration.waiting_phone)
    dp.message.register(cmd_menu, Command("menu"), F.chat.type == "private")
    dp.message.register(cmd_lang, Command("lang"), F.chat.type == "private")
    dp.callback_query.register(handle_change_language_private, F.data == "change_language_private")
    dp.message.register(
        cmd_start_group, Command("start"),
        F.chat.type.in_({"group", "supergroup"}),
    )
    dp.callback_query.register(handle_check_subscription, F.data == "check_subscription")
