"""Group-protection handlers: join/leave, warn commands, file/link scanning."""
import logging
import os
from datetime import datetime
import re
from urllib.parse import urlparse

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.container import Container
from app.controllers.filters import is_chat_admin
from app.core.bot import bot
from app.core.config import settings
from app.models import ScanVerdict
from app.services.link_extractor import extract_links
from app.views import formatters, keyboards
from app.views.texts import get_text
from app.repositories.base import get_conn
from app.states.states import GroupSettingsState

logger = logging.getLogger(__name__)

CARD_WARNING = {
    "uz": (
        "⚠️ <b>Diqqat! Guruhda plastik karta raqami aniqlandi!</b>\n\n"
        "Plastik kartangiz xavfsizligini ta'minlash uchun quyidagi qoidalarga qat'iy amal qiling:\n"
        "1️⃣ Kartangizning <b>CVV kodini</b> (orqa tomondagi 3 xonali son) va <b>amal qilish muddatini</b> hech kimga aytmang!\n"
        "2️⃣ Telefoningizga kelgan <b>SMS tasdiqlash kodini</b> hech qachon hech kimga ulashmang!\n"
        "3️⃣ SafeGuard bot sizdan hech qachon karta ma'lumotlarini so'ramaydi.\n\n"
        "🛡 <i>O'zingizni kiberfiribgarlardan asrang!</i>"
    ),
    "uz_cyr": (
        "⚠️ <b>Диққат! Гуруҳда пластик карта рақами аниқланди!</b>\n\n"
        "Пластик картангиз хавфсизлигини таъминлаш учун қуйидаги қоидаларга қатъий амал қилинг:\n"
        "1️⃣ Картангизнинг <b>CVV кодини</b> (орқа томондаги 3 хонали сон) ва <b>амал қилиш муддатини</b> ҳеч кимга айтманг!\n"
        "2️⃣ Телефонингизга келган <b>SMS тасдиқлаш кодини</b> ҳеч қачон ҳеч кимга улашманг!\n"
        "3️⃣ SafeGuard бот сиздан ҳеч қачон карта маълумотларини сўрамайди.\n\n"
        "🛡 <i>Ўзингизни киберфирибгарлардан асранг!</i>"
    ),
    "ru": (
        "⚠️ <b>Внимание! В группе обнаружен номер банковской карты!</b>\n\n"
        "Для обеспечения безопасности вашей карты строго соблюдайте следующие правила:\n"
        "1️⃣ Никогда и никому не сообщайте <b>CVV-код</b> (3-значное число на обратной стороне) и <b>срок действия</b> карты!\n"
        "2️⃣ Никогда не делитесь <b>SMS-кодом подтверждения</b>, который приходит на ваш телефон!\n"
        "3️⃣ SafeGuard бот никогда не запрашивает данные вашей карты.\n\n"
        "🛡 <i>Берегите себя от кибермошенников!</i>"
    ),
    "en": (
        "⚠️ <b>Attention! A bank card number has been detected in the group!</b>\n\n"
        "To ensure the security of your card, strictly follow these rules:\n"
        "1️⃣ Never share your card's <b>CVV code</b> (3-digit code on the back) and <b>expiration date</b> with anyone!\n"
        "2️⃣ Never share the <b>SMS confirmation code</b> sent to your phone!\n"
        "3️⃣ SafeGuard bot will never ask for your card details.\n\n"
        "🛡 <i>Protect yourself from cyber fraudsters!</i>"
    )
}


async def _safe_delete(msg: Message | None) -> None:
    if msg is None:
        return
    try:
        await msg.delete()
    except Exception:
        pass


async def _save_forensics_case(message: Message, violation_type: str, reason: str, c: Container) -> None:
    sender = message.from_user
    if not sender:
        return
    
    sender_id = sender.id
    full_name = sender.full_name
    username = sender.username or ""
    chat_id = message.chat.id
    chat_title = message.chat.title or "Guruh"
    message_text = message.text or message.caption or ""

    phone = ""
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT phone FROM users WHERE user_id = ?", (sender_id,)).fetchone()
            if row and row[0]:
                phone = row[0]
    except Exception as e:
        logger.warning(f"Forensika uchun telefon raqamini olishda xatolik: {e}")

    photo_path = None
    try:
        photos = await bot.get_user_profile_photos(user_id=sender_id, limit=1)
        if photos and photos.photos:
            file_id = photos.photos[0][-1].file_id
            file_info = await bot.get_file(file_id)
            
            photos_dir = os.path.join(settings.base_dir, "forensics_photos")
            os.makedirs(photos_dir, exist_ok=True)
            
            filename = f"user_{sender_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            full_path = os.path.join(photos_dir, filename)
            
            await bot.download(file_info, destination=full_path)
            
            photo_path = full_path
            logger.info(f"Huquqbuzar profil rasmi yuklab olindi: {photo_path}")
    except Exception as e:
        logger.warning(f"Huquqbuzar profil rasmini yuklab olishda xatolik (normal holat): {e}")

    try:
        case_id = c.forensics.save(
            chat_id=chat_id,
            chat_title=chat_title,
            user_id=sender_id,
            full_name=full_name,
            username=username,
            phone=phone,
            message_text=message_text,
            violation_type=violation_type,
            reason=reason,
            photo_path=photo_path
        )
        logger.info(f"Tergov dalillar arxivida saqlandi: Case ID #{case_id}")
    except Exception as e:
        logger.error(f"Tergov dalilini saqlashda xatolik: {e}")


def register(dp: Dispatcher, c: Container) -> None:
    group_filter = F.chat.type.in_({"group", "supergroup"})

    async def bot_added_to_group(update: ChatMemberUpdated):
        chat = update.chat
        new_status = update.new_chat_member.status
        if new_status in ("member", "administrator"):
            invite_link = ""
            can_invite = False
            try:
                bot_member = await bot.get_chat_member(chat.id, (await bot.get_me()).id)
                can_invite = getattr(bot_member, "can_invite_users", False)
                if can_invite:
                    chat_info = await bot.get_chat(chat.id)
                    invite_link = chat_info.invite_link or ""
                    if not invite_link:
                        link_obj = await bot.create_chat_invite_link(chat.id)
                        invite_link = link_obj.invite_link or ""
            except Exception:
                pass

            # Resolve default group language based on the user who added it
            added_by = update.from_user.id if update.from_user else 0
            default_lang = "uz"
            if added_by:
                default_lang = c.users.get_language(added_by)

            # Initialize settings with the default language
            c.groups.save(chat.id, chat.title or "Noma'lum", chat.username or "", invite_link, added_by)
            c.groups.update_custom_settings(
                chat.id,
                warnings_limit=3,
                custom_keywords="",
                whitelisted_domains="",
                language=default_lang
            )

            # ── Havola orqali taklif qilish o'chiq bo'lsa ──────────────
            if not can_invite and not invite_link:
                try:
                    await bot.send_message(
                        chat.id,
                        get_text("group_no_invite_link", default_lang),
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.warning("Invite link ogohlantirishni yuborishda xatolik: %s", e)
                try:
                    await bot.leave_chat(chat.id)
                    logger.info("Bot guruhdan chiqdi (invite link yo'q): %s", chat.id)
                except Exception as e:
                    logger.warning("Guruhdan chiqishda xatolik: %s", e)
                return

            # ── Havola bor → normal qo'shilish ─────────────────────────
            c.user_settings.set_group_mode(chat.id, True)

            try:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                btn_lbl = {
                    "uz": "📖 Yo'riqnoma / Qo'llanma",
                    "uz_cyr": "📖 Йўриқнома / Қўлланма",
                    "ru": "📖 Инструкция / Руководство",
                    "en": "📖 User Guide / Manual"
                }.get(default_lang, "📖 Guide")
                
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text=btn_lbl, url=f"https://t.me/{settings.bot_username}?start=help_group")
                ]])
                
                await bot.send_message(chat.id, get_text("group_added", default_lang), parse_mode="HTML", reply_markup=kb)
            except Exception as e:
                logger.warning("Guruh xush kelibsiz xabari yuborilmadi: %s", e)

        elif new_status in ("left", "kicked"):
            c.user_settings.set_group_mode(chat.id, False)
            c.groups.deactivate(chat.id)
        else:
            c.groups.update_info(chat.id, chat.title or "Noma'lum", chat.username or "")

    async def chat_updated(update: ChatMemberUpdated):
        chat = update.chat
        try:
            c.groups.update_info(chat.id, chat.title or "Noma'lum", chat.username or "")
        except Exception as e:
            logger.warning("Chat yangilashda xatolik: %s", e)

    async def cmd_enable(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        c.user_settings.set_group_mode(chat_id, True)
        
        enable_msg = {
            "uz": "✅ Guruh himoyasi YOQILDI!",
            "uz_cyr": "✅ Гуруҳ ҳимояси ЁҚИЛДИ!",
            "ru": "✅ Защита группы ВКЛЮЧЕНА!",
            "en": "✅ Group protection ENABLED!"
        }.get(lang, "")
        await message.answer(enable_msg)

    async def cmd_disable(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        c.user_settings.set_group_mode(chat_id, False)
        
        disable_msg = {
            "uz": "❌ Guruh himoyasi O'CHIRILDI.",
            "uz_cyr": "❌ Гуруҳ ҳимояси ЎЧИРИЛДИ.",
            "ru": "❌ Защита группы ОТКЛЮЧЕНА.",
            "en": "❌ Group protection DISABLED."
        }.get(lang, "")
        await message.answer(disable_msg)

    async def cmd_status(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        is_on = c.user_settings.get_group_mode(chat_id)
        
        status_on = {"uz": "Yoqiq", "uz_cyr": "Ёқиқ", "ru": "Включена", "en": "Enabled"}.get(lang, "Yoqiq")
        status_off = {"uz": "O'chiq", "uz_cyr": "Ўчиқ", "ru": "Отключена", "en": "Disabled"}.get(lang, "O'chiq")
        status_text = f"✅ {status_on}" if is_on else f"❌ {status_off}"
        
        status_msg = {
            "uz": f"🛡 Himoya: {status_text}",
            "uz_cyr": f"🛡 Ҳимоя: {status_text}",
            "ru": f"🛡 Защита: {status_text}",
            "en": f"🛡 Protection: {status_text}"
        }.get(lang, "")
        await message.answer(status_msg)

    async def cmd_warn(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        if not message.reply_to_message:
            warn_reply = {
                "uz": "⚠️ Warn berish uchun xabarga reply qiling!",
                "uz_cyr": "⚠️ Warn бериш учун хабарга reply қилинг!",
                "ru": "⚠️ Для выдачи предупреждения ответьте на сообщение пользователя!",
                "en": "⚠️ Reply to a message to issue a warning!"
            }.get(lang, "")
            await message.answer(warn_reply)
            return
            
        target = message.reply_to_message.from_user
        parts = (message.text or "").split(maxsplit=1)
        
        reason_default = {
            "uz": "Sabab ko'rsatilmadi",
            "uz_cyr": "Сабаб кўрсатилмади",
            "ru": "Причина не указана",
            "en": "No reason specified"
        }.get(lang, "")
        reason = parts[1] if len(parts) > 1 else reason_default
        
        limit = g_settings.get("warnings_limit", settings.max_warnings)
        await c.moderator.warn_or_ban(
            chat_id, target.id, target.full_name, reason, max_warns=limit, lang=lang
        )

    async def cmd_warns(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not message.reply_to_message:
            warns_reply = {
                "uz": "⚠️ Warnlarni ko'rish uchun xabarga reply qiling!",
                "uz_cyr": "⚠️ Warnларни кўриш учун хабарга reply қилинг!",
                "ru": "⚠️ Чтобы посмотреть предупреждения, ответьте на сообщение!",
                "en": "⚠️ Reply to a message to see warning count!"
            }.get(lang, "")
            await message.answer(warns_reply)
            return
            
        target = message.reply_to_message.from_user
        n = c.warnings.count(chat_id, target.id)
        limit = g_settings.get("warnings_limit", settings.max_warnings)
        await message.answer(
            f"📋 <b>{target.full_name}</b> — Warn: {n}/{limit}",
            parse_mode="HTML",
        )

    async def cmd_unwarn(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        if not message.reply_to_message:
            unwarn_reply = {
                "uz": "⚠️ Reply qiling!",
                "uz_cyr": "⚠️ Reply қилинг!",
                "ru": "⚠️ Ответьте на сообщение!",
                "en": "⚠️ Reply to a message!"
            }.get(lang, "")
            await message.answer(unwarn_reply)
            return
            
        target = message.reply_to_message.from_user
        c.warnings.clear(chat_id, target.id)
        
        unwarn_success = {
            "uz": f"✅ <b>{target.full_name}</b> warnlari tozalandi.",
            "uz_cyr": f"✅ <b>{target.full_name}</b> warnлари тозаланди.",
            "ru": f"✅ Предупреждения пользователя <b>{target.full_name}</b> сброшены.",
            "en": f"✅ Warnings for <b>{target.full_name}</b> have been cleared."
        }.get(lang, "")
        await message.answer(unwarn_success, parse_mode="HTML")

    async def cmd_group_lang(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        text = {
            "uz": "🌐 <b>Guruh tilini tanlang:</b>",
            "uz_cyr": "🌐 <b>Гуруҳ тилини танланг:</b>",
            "ru": "🌐 <b>Выберите язык группы:</b>",
            "en": "🌐 <b>Select group language:</b>"
        }.get(lang, "🌐")
        
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboards.group_language_selection_kb(chat_id, lang)
        )

    async def _sync_group_info(message: Message) -> None:
        """Guruh nomi yoki username o'zgarganida bazani yangilaydi."""
        try:
            chat = message.chat
            c.groups.update_info(chat.id, chat.title or "Noma'lum", chat.username or "")
        except Exception as e:
            logger.warning("Guruh ma'lumotlarini yangilashda xatolik: %s", e)

    async def handle_group_document(message: Message):
        chat_id = message.chat.id
        await _sync_group_info(message)
        if not c.user_settings.get_group_mode(chat_id):
            return
        
        filters = c.user_settings.get_group_settings(chat_id)
        if not filters.get("filter_files", True):
            return

        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")

        sender = message.from_user.first_name if message.from_user else "Noma'lum"
        sender_id = message.from_user.id if message.from_user else 0
        doc = message.document
        file_name = doc.file_name or "nomsiz_fayl"
        size_mb = doc.file_size / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            return

        wait_text = {
            "uz": "⏳ <b>Tekshirilmoqda...</b>\n🛡 Ochishga shoshilmang!",
            "uz_cyr": "⏳ <b>Текширилмоқда...</b>\n🛡 Очишга шошилманг!",
            "ru": "⏳ <b>Проверка...</b>\n🛡 Не спешите открывать!",
            "en": "⏳ <b>Scanning...</b>\n🛡 Do not open yet!"
        }.get(lang, "")
        wait = await message.reply(wait_text, parse_mode="HTML")
        try:
            import io
            downloaded = io.BytesIO()
            await bot.download(doc.file_id, destination=downloaded)
            file_bytes = downloaded.getvalue()
            result = await c.scanner.scan_file(sender_id, file_bytes, file_name)

            if result.verdict.is_bad:
                mention = formatters.mention(sender_id, sender)
                await _safe_delete(message)
                await _safe_delete(wait)
                await bot.send_message(
                    chat_id, formatters.dangerous_file_warning(result, mention, lang),
                    parse_mode="HTML",
                )
                await _save_forensics_case(message, "file", f"Antivirus xavfli deb topgan fayl yubordi: {file_name} ({result.malicious} ta tahdid)", c)
                limit = g_settings.get("warnings_limit", settings.max_warnings)
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Xavfli fayl yuborish", max_warns=limit, lang=lang)
            else:
                await _safe_delete(wait)
        except Exception as e:
            logger.error("Guruh fayl xatolik: %s", e)
            await _safe_delete(wait)

    async def check_content_violations(message: Message, text: str, filters: dict, sender_id: int, sender: str, mention: str) -> bool:
        if not text:
            return False

        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        limit = g_settings.get("warnings_limit", settings.max_warnings)

        # 0. Kiber-Qalqon Card Check (doesn't block message, just warns)
        card_pattern = r"\b(?:8600|9860|5614|4[0-9]{3}|5[0-9]{3}|6[0-9]{3})[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b"
        if re.search(card_pattern, text):
            try:
                await message.reply(CARD_WARNING.get(lang, CARD_WARNING["uz"]), parse_mode="HTML")
            except Exception as e:
                logger.warning(f"Karta haqida ogohlantirish yuborishda xato: {e}")

        # 1. Custom Keywords Check
        if filters.get("filter_nlp", True):
            custom_kws = [kw.strip().lower() for kw in g_settings.get("custom_keywords", "").split(",") if kw.strip()]
            text_lower = text.lower()
            matched_kws = [kw for kw in custom_kws if kw in text_lower]
            if matched_kws:
                await _safe_delete(message)
                
                kws_warn = {
                    "uz": f"🚫 <b>TAQIQLANGAN SO'Z ANIQLANDI!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Yuboruvchi: {mention}\n📝 Xabarda guruh uchun taqiqlangan so'z aniqlandi.\n\n<i>Tizim avtomatik ravishda xabarni o'chirdi.</i>",
                    "uz_cyr": f"🚫 <b>ТАҚИҚЛАНГАН СЎЗ АНИҚЛАНДИ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Юборувчи: {mention}\n📝 Xабарда гуруҳ учун тақиқланган сўз аниқланди.\n\n<i>Тизим автоматик равишда хабарни ўчирди.</i>",
                    "ru": f"🚫 <b>ОБНАРУЖЕНО ЗАПРЕЩЕННОЕ СЛОВО!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Отправитель: {mention}\n📝 В сообщении обнаружено запрещенное для группы слово.\n\n<i>Система автоматически удалила сообщение.</i>",
                    "en": f"🚫 <b>BANNED WORD DETECTED!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Sender: {mention}\n📝 A word banned for this group was detected in the message.\n\n<i>The system has automatically deleted the message.</i>"
                }.get(lang, "")
                
                await bot.send_message(
                    chat_id,
                    kws_warn,
                    parse_mode="HTML",
                )
                await _save_forensics_case(message, "bullying", f"Guruh qora ro'yxatidagi so'z(lar) topildi: {', '.join(matched_kws)}", c)
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, f"Taqiqlangan so'z ishlatish ({matched_kws[0]})", max_warns=limit, lang=lang)
                return True

        # 2. Spam check
        if filters.get("filter_nlp", True):
            if c.spam.is_spam(text):
                await _safe_delete(message)
                
                spam_warn = {
                    "uz": f"🚫 <b>SPAM ANIQLANDI VA BLOKLANDI!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Yuboruvchi: {mention}\n📝 Xabar tarkibida spam belgilari topildi.\n\n<i>Tizim avtomatik ravishda xabarni o'chirdi.</i>",
                    "uz_cyr": f"🚫 <b>СПАМ АНИҚЛАНДИ ВА БЛОКЛАНДИ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Юборувчи: {mention}\n📝 Хабар таркибида спам белгилари топилди.\n\n<i>Тизим автоматик равишда хабарни ўчирди.</i>",
                    "ru": f"🚫 <b>ОБНАРУЖЕН И ЗАБЛОКИРОВАН СПАМ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Отправитель: {mention}\n📝 В сообщении обнаружены признаки спама.\n\n<i>Система автоматически удалила сообщение.</i>",
                    "en": f"🚫 <b>SPAM DETECTED AND BLOCKED!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Sender: {mention}\n📝 Spam patterns were detected in the message.\n\n<i>The system has automatically deleted the message.</i>"
                }.get(lang, "")
                
                await bot.send_message(
                    chat_id,
                    spam_warn,
                    parse_mode="HTML",
                )
                await _save_forensics_case(message, "bullying", "Spam kalit so'zlar aniqlandi", c)
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Spam xabar yuborish", max_warns=limit, lang=lang)
                return True

        # 3. NLP check
        if filters.get("filter_nlp", True):
            nlp_res = await c.nlp.analyze_text(text)
            if nlp_res["is_violation"]:
                await _safe_delete(message)
                category = nlp_res["category"] or "other"
                reason = nlp_res["reason"]
                await bot.send_message(
                    chat_id,
                    formatters.nlp_violation_warning(category, reason, mention, lang),
                    parse_mode="HTML"
                )
                await _save_forensics_case(message, category, reason, c)
                
                reason_map = {
                    "uz": {
                        "extremism": "Diniy extremism va radikalizm targ'iboti",
                        "drugs": "Giyohvand moddalar yoki preparatlar yashirin savdosi/targ'iboti",
                        "bullying": "Kiberbulling, shaxsiyatga tegish yoki zo'ravonlik tahdidi",
                        "cybercrime": "Kiberfiribgarlik yoki moliyaviy fishing faoliyati"
                    },
                    "uz_cyr": {
                        "extremism": "Диний экстремизм ва радикализм тарғиботи",
                        "drugs": "Гиёҳванд моддалар ёки препаратлар яширин савдоси/тарғиботи",
                        "bullying": "Кибербуллинг, шахсиятга тегиш ёки зўравонлик таҳдиди",
                        "cybercrime": "Киберфирибгарлик ёки молиявий фишинг фаолияти"
                    },
                    "ru": {
                        "extremism": "Пропаганда религиозного экстремизма и радикализма",
                        "drugs": "Пропаганда или продажа наркотических средств",
                        "bullying": "Кибербуллинг, оскорбление личности или угрозы насилия",
                        "cybercrime": "Кибермошенничество или финансовый фишинг"
                    },
                    "en": {
                        "extremism": "Promotion of religious extremism and radicalism",
                        "drugs": "Promotion or trade of illegal drugs",
                        "bullying": "Cyberbullying, personal attack, or threat of violence",
                        "cybercrime": "Cyber-fraud or financial phishing activity"
                    }
                }.get(lang, {})
                moderator_reason = reason_map.get(category, f"Siyosat buzilishi: {reason}")
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, moderator_reason, max_warns=limit, lang=lang)
                return True

        # 4. Link check
        links = extract_links(message)
        if links and filters.get("filter_links", True):
            custom_wl = [d.strip().lower() for d in g_settings.get("whitelisted_domains", "").split(",") if d.strip()]
            
            scannable_links = []
            for url in links:
                scan_target = url
                if url.startswith("@"):
                    scan_target = f"https://t.me/{url.lstrip('@')}"
                elif ("t.me/" in url or "telegram.me/" in url) and not url.startswith(("http://", "https://")):
                    scan_target = f"https://{url}"

                parsed = urlparse(scan_target)
                domain = parsed.netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                
                is_whitelisted = False
                for wl_dom in custom_wl:
                    if domain == wl_dom or domain.endswith("." + wl_dom):
                        is_whitelisted = True
                        break
                
                if not is_whitelisted:
                    scannable_links.append((url, scan_target))

            if scannable_links:
                wait_text = {
                    "uz": "⏳ <b>Link tekshirilmoqda...</b>\n🛡 Ochishga shoshilmang!",
                    "uz_cyr": "⏳ <b>Линк текширилмоқда...</b>\n🛡 Очишга шошилманг!",
                    "ru": "⏳ <b>Ссылка проверяется...</b>\n🛡 Не спешите открывать!",
                    "en": "⏳ <b>Link is being scanned...</b>\n🛡 Do not open yet!"
                }.get(lang, "")
                wait = await message.reply(wait_text, parse_mode="HTML")
                any_bad = False
                for url, scan_target in scannable_links:
                    try:
                        if c.blacklist.exists(scan_target):
                            any_bad = True
                            await _safe_delete(message)
                            await _safe_delete(wait)
                            await bot.send_message(
                                chat_id, formatters.blacklisted_link_warning(mention, lang),
                                parse_mode="HTML",
                            )
                            await _save_forensics_case(message, "link", f"Qora ro'yxatdagi xavfli link yubordi: {url}", c)
                            await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Qora ro'yxatdagi link", max_warns=limit, lang=lang)
                            break

                        result = await c.scanner.scan_url(sender_id, scan_target)
                        if result.verdict.is_bad:
                            any_bad = True
                            await _safe_delete(message)
                            await _safe_delete(wait)
                            await bot.send_message(
                                chat_id, formatters.dangerous_link_warning(result, mention, lang),
                                parse_mode="HTML",
                            )
                            await _save_forensics_case(message, "link", f"Antivirus xavfli deb topgan link yubordi: {url} ({result.malicious} ta tahdid)", c)
                            await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Xavfli link yuborish", max_warns=limit, lang=lang)
                            break
                    except Exception as e:
                        logger.error("Guruh link xatolik: %s", e)

                if any_bad:
                    return True
                else:
                    await _safe_delete(wait)

        return False

    async def handle_group_message(message: Message):
        chat_id = message.chat.id
        await _sync_group_info(message)
        if not c.user_settings.get_group_mode(chat_id):
            return
        text = message.text or message.caption or ""
        if not text or text.startswith("/"):
            return

        sender = message.from_user.first_name if message.from_user else "Noma'lum"
        sender_id = message.from_user.id if message.from_user else 0
        mention = formatters.mention(sender_id, sender)
        filters = c.user_settings.get_group_settings(chat_id)

        if c.rate_limiter.hit(sender_id):
            return

        await check_content_violations(message, text, filters, sender_id, sender, mention)

    async def handle_group_photo(message: Message):
        chat_id = message.chat.id
        await _sync_group_info(message)
        if not c.user_settings.get_group_mode(chat_id):
            return
        
        filters = c.user_settings.get_group_settings(chat_id)
        if not filters.get("filter_links", True) and not filters.get("filter_nlp", True):
            return

        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")

        sender = message.from_user.first_name if message.from_user else "Noma'lum"
        sender_id = message.from_user.id if message.from_user else 0
        mention = formatters.mention(sender_id, sender)

        # 1. Scan caption for violations first
        caption = message.caption or ""
        if caption.strip():
            violation_handled = await check_content_violations(message, caption, filters, sender_id, sender, mention)
            if violation_handled:
                return

        # 2. Proceed with QR code scanner in photo
        photo = message.photo[-1]
        try:
            import io
            from app.services import decode_qr
            
            downloaded = io.BytesIO()
            await bot.download(photo.file_id, destination=downloaded)
            image_bytes = downloaded.getvalue()
            
            qr_data = decode_qr(image_bytes)
            if not qr_data:
                return
            
            limit = g_settings.get("warnings_limit", settings.max_warnings)
            
            if qr_data.startswith(("http://", "https://")):
                if not filters.get("filter_links", True):
                    return
                
                # Whitelisted domains check
                custom_wl = [d.strip().lower() for d in g_settings.get("whitelisted_domains", "").split(",") if d.strip()]
                parsed = urlparse(qr_data)
                domain = parsed.netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                
                is_whitelisted = False
                for wl_dom in custom_wl:
                    if domain == wl_dom or domain.endswith("." + wl_dom):
                        is_whitelisted = True
                        break
                
                if is_whitelisted:
                    white_reply = {
                        "uz": f"🔍 <b>Rasmdan QR-kod aniqlandi!</b>\n🔗 Havola: <code>{qr_data}</code>\n✅ Havola oq ro'yxatda (ishonchli).",
                        "uz_cyr": f"🔍 <b>Расмдан QR-код аниқланди!</b>\n🔗 Ҳавола: <code>{qr_data}</code>\n✅ Ҳавола оқ рўйхатда (ишончли).",
                        "ru": f"🔍 <b>На изображении обнаружен QR-код!</b>\n🔗 Ссылка: <code>{qr_data}</code>\n✅ Ссылка в белом списке (доверенная).",
                        "en": f"🔍 <b>QR-code detected on image!</b>\n🔗 Link: <code>{qr_data}</code>\n✅ Link is whitelisted (trusted)."
                    }.get(lang, "")
                    await message.reply(white_reply, parse_mode="HTML")
                    return
                
                if c.blacklist.exists(qr_data):
                    await _safe_delete(message)
                    
                    black_qr_msg = {
                        "uz": f"🚨 <b>XAVFLI QR-KOD BLOKLANDI!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Yuboruvchi: {mention}\n🔗 Havola: {qr_data[:50]}...\n📋 Qora ro'yxatda mavjud!",
                        "uz_cyr": f"🚨 <b>ХАВФЛИ QR-КОД БЛОКЛАНДИ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Юборувчи: {mention}\n🔗 Ҳавола: {qr_data[:50]}...\n📋 Қора рўйхатда мавжуд!",
                        "ru": f"🚨 <b>ОПАСНЫЙ QR-КОД ЗАБЛОКИРОВАН!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Отправитель: {mention}\n🔗 Ссылка: {qr_data[:50]}...\n📋 Присутствует в черном списке!",
                        "en": f"🚨 <b>DANGEROUS QR-CODE BLOCKED!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Sender: {mention}\n🔗 Link: {qr_data[:50]}...\n📋 Exists in blacklist!"
                    }.get(lang, "")
                    
                    await bot.send_message(
                        chat_id,
                        black_qr_msg,
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, "link", f"QR-kod orqali qora ro'yxatdagi xavfli link yubordi: {qr_data}", c)
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, "QR-kod orqali xavfli link tarqatish", max_warns=limit, lang=lang)
                    return
                
                result = await c.scanner.scan_url(sender_id, qr_data)
                if result.verdict.is_bad:
                    await _safe_delete(message)
                    
                    bad_qr_msg = {
                        "uz": f"🚨 <b>XAVFLI QR-KOD BLOKLANDI!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Yuboruvchi: {mention}\n🔗 Havola: {qr_data[:50]}...\n\n{formatters.scan_result(result, lang)}",
                        "uz_cyr": f"🚨 <b>ХАВФЛИ QR-КОД БЛОКЛАНДИ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Юборувчи: {mention}\n🔗 Ҳавола: {qr_data[:50]}...\n\n{formatters.scan_result(result, lang)}",
                        "ru": f"🚨 <b>ОПАСНЫЙ QR-КОД ЗАБЛОКИРОВАН!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Отправитель: {mention}\n🔗 Ссылка: {qr_data[:50]}...\n\n{formatters.scan_result(result, lang)}",
                        "en": f"🚨 <b>DANGEROUS QR-CODE BLOCKED!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Sender: {mention}\n🔗 Link: {qr_data[:50]}...\n\n{formatters.scan_result(result, lang)}"
                    }.get(lang, "")
                    
                    await bot.send_message(
                        chat_id,
                        bad_qr_msg,
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, "link", f"QR-kod orqali antivirus aniqlagan xavfli link yubordi: {qr_data} ({result.malicious} ta tahdid)", c)
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, "QR-kod orqali xavfli link tarqatish", max_warns=limit, lang=lang)
                else:
                    safe_qr_msg = {
                        "uz": f"🔍 <b>Rasmdan QR-kod aniqlandi!</b>\n🔗 Havola: <code>{qr_data}</code>\n✅ Havola xavfsiz topildi.",
                        "uz_cyr": f"🔍 <b>Расмдан QR-код аниқланди!</b>\n🔗 Ҳавола: <code>{qr_data}</code>\n✅ Ҳавола хавфсиз топилди.",
                        "ru": f"🔍 <b>На изображении обнаружен QR-код!</b>\n🔗 Ссылка: <code>{qr_data}</code>\n✅ Ссылка признана безопасной.",
                        "en": f"🔍 <b>QR-code detected on image!</b>\n🔗 Link: <code>{qr_data}</code>\n✅ Link is safe."
                    }.get(lang, "")
                    await message.reply(safe_qr_msg, parse_mode="HTML")
            else:
                if not filters.get("filter_nlp", True):
                    return
                
                nlp_res = await c.nlp.analyze_text(qr_data)
                if nlp_res["is_violation"]:
                    await _safe_delete(message)
                    category = nlp_res["category"] or "other"
                    reason = nlp_res["reason"]
                    
                    banned_qr_msg = {
                        "uz": f"🚨 <b>TAQIQLANGAN QR-KOD BLOKLANDI!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Yuboruvchi: {mention}\n📂 Kategoriya: <code>{category.upper()}</code>\n📝 Izoh: <i>{reason}</i>",
                        "uz_cyr": f"🚨 <b>ТАҚИҚЛАНГАН QR-КОД БЛОКЛАНДИ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Юборувчи: {mention}\n📂 Категория: <code>{category.upper()}</code>\n📝 Изоҳ: <i>{reason}</i>",
                        "ru": f"🚨 <b>ЗАПРЕЩЕННЫЙ QR-КОД ЗАБЛОКИРОВАН!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Отправитель: {mention}\n📂 Категория: <code>{category.upper()}</code>\n📝 Примечание: <i>{reason}</i>",
                        "en": f"🚨 <b>BANNED QR-CODE BLOCKED!</b>\n━━━━━━━━━━━━━━━━━━━━━\n👤 Sender: {mention}\n📂 Category: <code>{category.upper()}</code>\n📝 Reason: <i>{reason}</i>"
                    }.get(lang, "")
                    
                    await bot.send_message(
                        chat_id,
                        banned_qr_msg,
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, category, f"QR-kod matnidan qoidabuzarlik topildi: {qr_data[:100]}", c)
                    
                    reason_map = {
                        "uz": {
                            "extremism": "QR-kod orqali diniy extremism/radikalizm",
                            "drugs": "QR-kod orqali giyohvandlik targ'iboti",
                            "bullying": "QR-kod orqali kiberbulling/haqorat",
                            "cybercrime": "QR-kod orqali kiberfiribgarlik/fishing"
                        },
                        "uz_cyr": {
                            "extremism": "QR-код орқали диний экстремизм/радикализм",
                            "drugs": "QR-код орқали гиёҳвандлик тарғиботи",
                            "bullying": "QR-код орқали кибербуллинг/ҳақорат",
                            "cybercrime": "QR-код орқали киберфирибгарлик/фишинг"
                        },
                        "ru": {
                            "extremism": "Религиозный экстремизм/радикализм через QR-код",
                            "drugs": "Пропаганда наркотиков через QR-код",
                            "bullying": "Кибербуллинг/оскорбление через QR-код",
                            "cybercrime": "Кибермошенничество/фишинг через QR-код"
                        },
                        "en": {
                            "extremism": "Religious extremism/radicalism via QR-code",
                            "drugs": "Drug promotion via QR-code",
                            "bullying": "Cyberbullying/harassment via QR-code",
                            "cybercrime": "Cyber-fraud/phishing via QR-code"
                        }
                    }.get(lang, {})
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, reason_map.get(category, f"QR-kod qoidabuzarligi: {reason}"), max_warns=limit, lang=lang)
                else:
                    safe_txt_msg = {
                        "uz": f"🔍 <b>Rasmdan QR-kod aniqlandi!</b>\n📝 Matn: <code>{qr_data}</code>\n✅ Matn xavfsiz topildi.",
                        "uz_cyr": f"🔍 <b>Расмдан QR-код аниқланди!</b>\n📝 Матн: <code>{qr_data}</code>\n✅ Матн хавфсиз топилди.",
                        "ru": f"🔍 <b>На изображении обнаружен QR-код!</b>\n📝 Текст: <code>{qr_data}</code>\n✅ Текст признан безопасным.",
                        "en": f"🔍 <b>QR-code detected on image!</b>\n📝 Text: <code>{qr_data}</code>\n✅ Text is safe."
                    }.get(lang, "")
                    await message.reply(safe_txt_msg, parse_mode="HTML")
                    
        except Exception as e:
            logger.error("Guruh rasm/QR xato: %s", e)

    async def cmd_settings(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        chat_title = message.chat.title or "Guruh"
        filters = c.user_settings.get_group_settings(chat_id)
        await message.answer(
            formatters.group_settings_text(chat_title, filters, g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters, g_settings, lang)
        )

    async def cmd_getlink(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await is_chat_admin(message):
            await message.answer(get_text("group_admin_only", lang))
            return
            
        try:
            chat_info = await bot.get_chat(chat_id)
            invite_link = chat_info.invite_link or ""
            if not invite_link:
                link_obj = await bot.create_chat_invite_link(chat_id)
                invite_link = link_obj.invite_link or ""
            if invite_link:
                c.groups.update_info(
                    chat_id,
                    chat_info.title or "Noma'lum",
                    chat_info.username or "",
                    invite_link
                )
                success_link = {
                    "uz": f"✅ <b>Invite link saqlandi!</b>\n\n🔗 {invite_link}\n\n<i>Endi «Guruhlarim» bo'limida guruh nomiga bosib kirish mumkin.</i>",
                    "uz_cyr": f"✅ <b>Invite link сақланди!</b>\n\n🔗 {invite_link}\n\n<i>Энди «Гуруҳларим» бўлимида гуруҳ номига босиб кириш мумкин.</i>",
                    "ru": f"✅ <b>Инвайт-ссылка сохранена!</b>\n\n🔗 {invite_link}\n\n<i>Теперь вы можете перейти в группу, кликнув по ее названию в меню «Мои группы».</i>",
                    "en": f"✅ <b>Invite link saved!</b>\n\n🔗 {invite_link}\n\n<i>Now you can access this group from the 'My Groups' section.</i>"
                }.get(lang, "")
                await message.answer(success_link, parse_mode="HTML")
            else:
                fail_link = {
                    "uz": "❌ Invite link yaratib bo'lmadi. Bot admin ekanligini tekshiring!",
                    "uz_cyr": "❌ Invite link яратиб бўлмади. Бот админ эканлигини текширинг!",
                    "ru": "❌ Не удалось создать инвайт-ссылку. Проверьте, является ли бот администратором!",
                    "en": "❌ Failed to create invite link. Verify if the bot is an administrator!"
                }.get(lang, "")
                await message.answer(fail_link)
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

    async def handle_toggle_gset(call: CallbackQuery):
        chat_id = call.message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        try:
            member = await bot.get_chat_member(chat_id, call.from_user.id)
            if member.status not in ("administrator", "creator") and call.from_user.id != settings.admin_id:
                err_admin = {
                    "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                    "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                    "ru": "Эту кнопку могут нажимать только администраторы группы!",
                    "en": "Only group administrators can press this button!"
                }.get(lang, "")
                await call.answer(err_admin, show_alert=True)
                return
        except Exception:
            pass

        raw = call.data.replace("toggle_gset_", "")
        parts = raw.split("_filter_")
        if len(parts) < 2:
            await call.answer()
            return
        target_chat_id = int(parts[0])
        filter_name = f"filter_{parts[1]}"

        filters = c.user_settings.get_group_settings(target_chat_id)
        current_val = filters.get(filter_name, True)
        new_val = not current_val
        c.user_settings.set_group_filter(target_chat_id, filter_name, new_val)

        updated_filters = c.user_settings.get_group_settings(target_chat_id)
        g_settings = c.groups.get_custom_settings(target_chat_id)
        chat_title = call.message.chat.title or "Guruh"
        
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, updated_filters, g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(target_chat_id, updated_filters, g_settings, lang)
        )
        
        alert_confirm = {
            "uz": "Sozlama o'zgartirildi!",
            "uz_cyr": "Созлама ўзгартирилди!",
            "ru": "Настройка изменена!",
            "en": "Setting updated!"
        }.get(lang, "")
        await call.answer(alert_confirm)

    async def _is_admin_or_owner(call: CallbackQuery, target_chat_id: int) -> bool:
        try:
            member = await bot.get_chat_member(target_chat_id, call.from_user.id)
            if member.status in ("administrator", "creator") or call.from_user.id == settings.admin_id:
                return True
        except Exception:
            pass
        return False

    async def handle_warn_dec(call: CallbackQuery):
        chat_id = int(call.data.replace("gset_warn_dec_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        limit = max(1, g_settings.get("warnings_limit", 3) - 1)
        c.groups.set_warnings_limit(chat_id, limit)
        
        filters = c.user_settings.get_group_settings(chat_id)
        updated_g_settings = c.groups.get_custom_settings(chat_id)
        chat_title = call.message.chat.title or "Guruh"
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, filters, updated_g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters, updated_g_settings, lang)
        )
        
        confirm = {
            "uz": f"Ogohlantirish limiti {limit} qilib belgilandi!",
            "uz_cyr": f"Огоҳлантириш лимити {limit} қилиб белгиланди!",
            "ru": f"Лимит предупреждений установлен на {limit}!",
            "en": f"Warnings limit set to {limit}!"
        }.get(lang, "")
        await call.answer(confirm)

    async def handle_warn_inc(call: CallbackQuery):
        chat_id = int(call.data.replace("gset_warn_inc_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        limit = min(10, g_settings.get("warnings_limit", 3) + 1)
        c.groups.set_warnings_limit(chat_id, limit)
        
        filters = c.user_settings.get_group_settings(chat_id)
        updated_g_settings = c.groups.get_custom_settings(chat_id)
        chat_title = call.message.chat.title or "Guruh"
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, filters, updated_g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters, updated_g_settings, lang)
        )
        
        confirm = {
            "uz": f"Ogohlantirish limiti {limit} qilib belgilandi!",
            "uz_cyr": f"Огоҳлантириш лимити {limit} қилиб белгиланди!",
            "ru": f"Лимит предупреждений установлен на {limit}!",
            "en": f"Warnings limit set to {limit}!"
        }.get(lang, "")
        await call.answer(confirm)

    async def handle_gset_lang_menu(call: CallbackQuery):
        chat_id = int(call.data.replace("gset_lang_menu_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        await call.answer()
        
        text = {
            "uz": "🌐 <b>Guruh tilini tanlang:</b>",
            "uz_cyr": "🌐 <b>Гуруҳ тилини танланг:</b>",
            "ru": "🌐 <b>Выберите язык группы:</b>",
            "en": "🌐 <b>Select group language:</b>"
        }.get(lang, "🌐")
        
        await call.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboards.group_language_selection_kb(chat_id, lang)
        )

    async def handle_gset_setlang(call: CallbackQuery):
        raw = call.data.replace("gset_setlang_", "")
        parts = raw.split("_")
        chat_id = int(parts[0])
        lang = parts[1]
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        c.groups.set_language(chat_id, lang)
        
        confirm = {
            "uz": "✅ Guruh tili o'zgartirildi!",
            "uz_cyr": "✅ Гуруҳ тили ўзгартирилди!",
            "ru": "✅ Язык группы изменен!",
            "en": "✅ Group language changed!"
        }.get(lang, "✅")
        await call.answer(confirm)
        
        filters = c.user_settings.get_group_settings(chat_id)
        g_settings = c.groups.get_custom_settings(chat_id)
        chat_title = call.message.chat.title or "Guruh"
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, filters, g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters, g_settings, lang)
        )

    async def handle_gset_back(call: CallbackQuery):
        chat_id = int(call.data.replace("group_settings_back_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        await call.answer()
        
        filters = c.user_settings.get_group_settings(chat_id)
        chat_title = call.message.chat.title or "Guruh"
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, filters, g_settings, lang),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters, g_settings, lang)
        )

    async def handle_edit_kws(call: CallbackQuery, state: FSMContext):
        chat_id = int(call.data.replace("gset_edit_kws_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        await call.answer()
        await state.update_data(settings_chat_id=chat_id)
        await state.set_state(GroupSettingsState.waiting_keywords)
        
        kws_prompt = {
            "uz": "✍️ <b>Guruh uchun taqiqlangan kalit so'zlarni kiriting:</b>\n\nSo'zlarni vergul bilan ajratib yozing (masalan: <i>reklama, aksiya, bonus</i>).\nMavjud taqiqlangan so'zlarni tozalash uchun <code>tozalash</code> deb yozing.\n\n<i>Bekor qilish uchun /cancel deb yozing.</i>",
            "uz_cyr": "✍️ <b>Гуруҳ учун тақиқланган калит сўзларни киритинг:</b>\n\nСўзларни вергул билан ажратиб ёзинг (масалан: <i>reklama, aksiya, bonus</i>).\nМавжуд тақиқланган сўзларни тозалаш учун <code>tozalash</code> деб ёзинг.\n\n<i>Бекор қилиш учун /cancel деб ёзинг.</i>",
            "ru": "✍️ <b>Введите запрещенные ключевые слова для группы:</b>\n\nРазделяйте слова запятыми (например: <i>реклама, акция, бонус</i>).\nЧтобы очистить текущие слова, введите <code>tozalash</code>.\n\n<i>Для отмены введите /cancel.</i>",
            "en": "✍️ <b>Enter banned keywords for the group:</b>\n\nSeparate words with commas (e.g., <i>ads, promo, bonus</i>).\nTo clear all banned words, type <code>tozalash</code>.\n\n<i>To cancel, type /cancel.</i>"
        }.get(lang, "")
        await call.message.answer(kws_prompt, parse_mode="HTML")

    async def handle_edit_wl(call: CallbackQuery, state: FSMContext):
        chat_id = int(call.data.replace("gset_edit_wl_", ""))
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        if not await _is_admin_or_owner(call, chat_id):
            err_admin = {
                "uz": "Bu tugmani faqat guruh adminlari bosa oladi!",
                "uz_cyr": "Бу тугмани фақат гуруҳ админлари боса олади!",
                "ru": "Эту кнопку могут нажимать только администраторы группы!",
                "en": "Only group administrators can press this button!"
            }.get(lang, "")
            await call.answer(err_admin, show_alert=True)
            return
            
        await call.answer()
        await state.update_data(settings_chat_id=chat_id)
        await state.set_state(GroupSettingsState.waiting_whitelist)
        
        wl_prompt = {
            "uz": "✍️ <b>Guruh uchun oq ro'yxatdagi domenlarni kiriting:</b>\n\nDomenlarni vergul bilan ajratib yozing (masalan: <i>kun.uz, google.com, daryo.uz</i>).\nOq ro'yxatni tozalash uchun <code>tozalash</code> deb yozing.\n\n<i>Bekor qilish uchun /cancel deb yozing.</i>",
            "uz_cyr": "✍️ <b>Гуруҳ учун оқ рўйхатдаги доменларни киритинг:</b>\n\nДоменларни вергул билан ажратиб ёзинг (масалан: <i>kun.uz, google.com, daryo.uz</i>).\nОқ рўйхатни тозалаш учун <code>tozalash</code> деб ёзинг.\n\n<i>Бекор қилиш учун /cancel деб ёзинг.</i>",
            "ru": "✍️ <b>Введите домены для белого списка группы:</b>\n\nРазделяйте домены запятыми (например: <i>kun.uz, google.com, daryo.uz</i>).\nЧтобы очистить белый список, введите <code>tozalash</code>.\n\n<i>Для отмены введите /cancel.</i>",
            "en": "✍️ <b>Enter domains for group whitelist:</b>\n\nSeparate domains with commas (e.g., <i>kun.uz, google.com, daryo.uz</i>).\nTo clear whitelist, type <code>tozalash</code>.\n\n<i>To cancel, type /cancel.</i>"
        }.get(lang, "")
        await call.message.answer(wl_prompt, parse_mode="HTML")

    async def process_kws_input(message: Message, state: FSMContext):
        text = message.text or ""
        data = await state.get_data()
        chat_id = data.get("settings_chat_id")
        if not chat_id:
            await state.clear()
            return
            
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")

        if text.strip().lower() == "/cancel":
            await state.clear()
            cancel_lbl = {"uz": "❌ Sozlash bekor qilindi.", "uz_cyr": "❌ Созлаш бекор қилинди.", "ru": "❌ Настройка отменена.", "en": "❌ Setup cancelled."}.get(lang, "")
            await message.reply(cancel_lbl)
            return
            
        if text.strip().lower() == "tozalash":
            c.groups.set_custom_keywords(chat_id, "")
            success_lbl = {"uz": "✅ Guruh taqiqlangan kalit so'zlari tozalandi!", "uz_cyr": "✅ Гуруҳ тақиқланган калит сўзлари тозаланди!", "ru": "✅ Запрещенные слова группы очищены!", "en": "✅ Group banned keywords cleared!"}.get(lang, "")
            await message.reply(success_lbl)
        else:
            kws = ",".join([w.strip() for w in text.split(",") if w.strip()])
            c.groups.set_custom_keywords(chat_id, kws)
            success_save = {
                "uz": f"✅ Guruh taqiqlangan kalit so'zlari saqlandi: <code>{kws}</code>",
                "uz_cyr": f"✅ Гуруҳ тақиқланган калит сўзлари сақланди: <code>{kws}</code>",
                "ru": f"✅ Запрещенные слова группы сохранены: <code>{kws}</code>",
                "en": f"✅ Group banned keywords saved: <code>{kws}</code>"
            }.get(lang, "")
            await message.reply(success_save, parse_mode="HTML")
            
        await state.clear()

    async def process_wl_input(message: Message, state: FSMContext):
        text = message.text or ""
        data = await state.get_data()
        chat_id = data.get("settings_chat_id")
        if not chat_id:
            await state.clear()
            return
            
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")

        if text.strip().lower() == "/cancel":
            await state.clear()
            cancel_lbl = {"uz": "❌ Sozlash bekor qilindi.", "uz_cyr": "❌ Созлаш бекор қилинди.", "ru": "❌ Настройка отменена.", "en": "❌ Setup cancelled."}.get(lang, "")
            await message.reply(cancel_lbl)
            return
            
        if text.strip().lower() == "tozalash":
            c.groups.set_whitelisted_domains(chat_id, "")
            success_lbl = {"uz": "✅ Guruh oq ro'yxati tozalandi!", "uz_cyr": "✅ Гуруҳ оқ рўйхати тозаланди!", "ru": "✅ Белый список группы очищен!", "en": "✅ Group whitelist cleared!"}.get(lang, "")
            await message.reply(success_lbl)
        else:
            domains = ",".join([d.strip().lower() for d in text.split(",") if d.strip()])
            c.groups.set_whitelisted_domains(chat_id, domains)
            success_save = {
                "uz": f"✅ Guruh oq ro'yxati saqlandi: <code>{domains}</code>",
                "uz_cyr": f"✅ Гуруҳ оқ рўйхати сақланди: <code>{domains}</code>",
                "ru": f"✅ Белый список группы сохранен: <code>{domains}</code>",
                "en": f"✅ Group whitelist saved: <code>{domains}</code>"
            }.get(lang, "")
            await message.reply(success_save, parse_mode="HTML")
            
        await state.clear()

    async def handle_close_gset(call: CallbackQuery):
        await call.message.delete()
        await call.answer()


    dp.my_chat_member.register(bot_added_to_group)
    dp.chat_member.register(chat_updated)
    dp.message.register(cmd_enable, Command("enable"), group_filter)
    dp.message.register(cmd_disable, Command("disable"), group_filter)
    dp.message.register(cmd_status, Command("status"), group_filter)
    dp.message.register(cmd_settings, Command("settings"), group_filter)
    dp.message.register(cmd_getlink, Command("getlink"), group_filter)
    dp.message.register(cmd_warn, Command("warn"), group_filter)
    dp.message.register(cmd_warns, Command("warns"), group_filter)
    dp.message.register(cmd_unwarn, Command("unwarn"), group_filter)
    dp.message.register(cmd_group_lang, Command("lang"), group_filter)

    dp.message.register(handle_group_document, F.document, group_filter)
    dp.message.register(handle_group_photo, F.photo, group_filter)
    dp.message.register(handle_group_message, group_filter)

    dp.callback_query.register(handle_toggle_gset, F.data.startswith("toggle_gset_"))
    dp.callback_query.register(handle_close_gset, F.data == "close_group_settings")
    dp.callback_query.register(handle_warn_dec, F.data.startswith("gset_warn_dec_"))
    dp.callback_query.register(handle_warn_inc, F.data.startswith("gset_warn_inc_"))
    dp.callback_query.register(handle_edit_kws, F.data.startswith("gset_edit_kws_"))
    dp.callback_query.register(handle_edit_wl, F.data.startswith("gset_edit_wl_"))
    dp.callback_query.register(handle_gset_lang_menu, F.data.startswith("gset_lang_menu_"))
    dp.callback_query.register(handle_gset_setlang, F.data.startswith("gset_setlang_"))
    dp.callback_query.register(handle_gset_back, F.data.startswith("group_settings_back_"))
    dp.message.register(process_kws_input, GroupSettingsState.waiting_keywords)
    dp.message.register(process_wl_input, GroupSettingsState.waiting_whitelist)
