"""Group-protection handlers: join/leave, warn commands, file/link scanning."""
import logging
import os
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, Message, CallbackQuery

from app.container import Container
from app.controllers.filters import is_chat_admin
from app.core.bot import bot
from app.core.config import settings
from app.models import ScanVerdict
from app.services import extract_links
from app.views import formatters, keyboards
from app.views.texts import GROUP_ADDED, GROUP_ADMIN_ONLY, GROUP_NO_INVITE_LINK
from app.repositories.base import get_conn

logger = logging.getLogger(__name__)


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
            
            # Use standard and robust aiogram 3.x download method
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

            # ── Havola orqali taklif qilish o'chiq bo'lsa ──────────────
            # Bot ishlay olmaydi — ogohlantirish yuborib, guruhdan chiqib ketadi
            if not can_invite and not invite_link:
                try:
                    await bot.send_message(
                        chat.id,
                        GROUP_NO_INVITE_LINK,
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.warning("Invite link ogohlantirishni yuborishda xatolik: %s", e)
                # Guruhdan chiqib ketish
                try:
                    await bot.leave_chat(chat.id)
                    logger.info("Bot guruhdan chiqdi (invite link yo'q): %s", chat.id)
                except Exception as e:
                    logger.warning("Guruhdan chiqishda xatolik: %s", e)
                return

            # ── Havola bor → normal qo'shilish ─────────────────────────
            c.user_settings.set_group_mode(chat.id, True)
            # Guruhga kimni qo'shganini saqlaymiz
            added_by = update.from_user.id if update.from_user else 0
            c.groups.save(chat.id, chat.title or "Noma'lum", chat.username or "", invite_link, added_by)

            try:
                await bot.send_message(chat.id, GROUP_ADDED, parse_mode="HTML")
            except Exception as e:
                logger.warning("Guruh xush kelibsiz xabari yuborilmadi: %s", e)

        elif new_status in ("left", "kicked"):
            c.user_settings.set_group_mode(chat.id, False)
            c.groups.deactivate(chat.id)
        else:
            c.groups.update_info(chat.id, chat.title or "Noma'lum", chat.username or "")

    async def chat_updated(update: ChatMemberUpdated):
        """Guruh nomi, username o'zgarganda avtomatik yangilash."""
        chat = update.chat
        try:
            c.groups.update_info(chat.id, chat.title or "Noma'lum", chat.username or "")
        except Exception as e:
            logger.warning("Chat yangilashda xatolik: %s", e)

    async def cmd_enable(message: Message):
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        c.user_settings.set_group_mode(message.chat.id, True)
        await message.answer("✅ Guruh himoyasi YOQILDI!")

    async def cmd_disable(message: Message):
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        c.user_settings.set_group_mode(message.chat.id, False)
        await message.answer("❌ Guruh himoyasi O'CHIRILDI.")

    async def cmd_status(message: Message):
        is_on = c.user_settings.get_group_mode(message.chat.id)
        await message.answer("🛡 Himoya: " + ("✅ Yoqiq" if is_on else "❌ Ochiq"))

    async def cmd_warn(message: Message):
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        if not message.reply_to_message:
            await message.answer("⚠️ Warn berish uchun xabarga reply qiling!")
            return
        target = message.reply_to_message.from_user
        parts = (message.text or "").split(maxsplit=1)
        reason = parts[1] if len(parts) > 1 else "Sabab ko'rsatilmadi"
        await c.moderator.warn_or_ban(
            message.chat.id, target.id, target.full_name, reason
        )

    async def cmd_warns(message: Message):
        if not message.reply_to_message:
            await message.answer("⚠️ Warnlarni ko'rish uchun xabarga reply qiling!")
            return
        target = message.reply_to_message.from_user
        n = c.warnings.count(message.chat.id, target.id)
        await message.answer(
            f"📋 <b>{target.full_name}</b> — Warn: {n}/{settings.max_warnings}",
            parse_mode="HTML",
        )

    async def cmd_unwarn(message: Message):
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        if not message.reply_to_message:
            await message.answer("⚠️ Reply qiling!")
            return
        target = message.reply_to_message.from_user
        c.warnings.clear(message.chat.id, target.id)
        await message.answer(
            f"✅ <b>{target.full_name}</b> warnlari tozalandi.", parse_mode="HTML"
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
        
        # Check files settings filter
        filters = c.user_settings.get_group_settings(chat_id)
        if not filters.get("filter_files", True):
            return

        sender = message.from_user.first_name if message.from_user else "Noma'lum"
        sender_id = message.from_user.id if message.from_user else 0
        doc = message.document
        file_name = doc.file_name or "nomsiz_fayl"
        size_mb = doc.file_size / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            return

        wait = await message.reply(
            "⏳ <b>Tekshirilmoqda...</b>\n🛡 Ochishga shoshilmang!", parse_mode="HTML"
        )
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
                    chat_id, formatters.dangerous_file_warning(result, mention),
                    parse_mode="HTML",
                )
                await _save_forensics_case(message, "file", f"Antivirus xavfli deb topgan fayl yubordi: {file_name} ({result.malicious} ta tahdid)", c)
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Xavfli fayl yuborish")
            else:
                await _safe_delete(wait)
        except Exception as e:
            logger.error("Guruh fayl xatolik: %s", e)
            await _safe_delete(wait)

    async def check_content_violations(message: Message, text: str, filters: dict, sender_id: int, sender: str, mention: str) -> bool:
        if not text:
            return False

        # 1. Spam check
        if filters.get("filter_nlp", True):
            if c.spam.is_spam(text):
                await _safe_delete(message)
                await bot.send_message(
                    message.chat.id,
                    f"🚫 <b>SPAM ANIQLANDI VA BLOKLANDI!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 Yuboruvchi: {mention}\n"
                    f"📝 Xabar tarkibida spam belgilari topildi.\n\n"
                    f"<i>Tizim avtomatik ravishda xabarni o'chirdi.</i>",
                    parse_mode="HTML",
                )
                await _save_forensics_case(message, "bullying", "Spam kalit so'zlar aniqlandi", c)
                await c.moderator.warn_or_ban(message.chat.id, sender_id, sender, "Spam xabar yuborish")
                return True

        # 2. NLP check
        if filters.get("filter_nlp", True):
            nlp_res = await c.nlp.analyze_text(text)
            if nlp_res["is_violation"]:
                await _safe_delete(message)
                category = nlp_res["category"] or "other"
                reason = nlp_res["reason"]
                await bot.send_message(
                    message.chat.id,
                    formatters.nlp_violation_warning(category, reason, mention),
                    parse_mode="HTML"
                )
                await _save_forensics_case(message, category, reason, c)
                reason_map = {
                    "extremism": "Diniy extremism va radikalizm targ'iboti",
                    "drugs": "Giyohvand moddalar yoki preparatlar yashirin savdosi/targ'iboti",
                    "bullying": "Kiberbulling, shaxsiyatga tegish yoki zo'ravonlik tahdidi"
                }
                moderator_reason = reason_map.get(category, f"Siyosat buzilishi: {reason}")
                await c.moderator.warn_or_ban(message.chat.id, sender_id, sender, moderator_reason)
                return True

        # 3. Link check
        links = extract_links(message)
        if links and filters.get("filter_links", True):
            wait = await message.reply(
                "⏳ <b>Link tekshirilmoqda...</b>\n🛡 Ochishga shoshilmang!", parse_mode="HTML"
            )
            any_bad = False
            for url in links:
                try:
                    scan_target = url
                    if url.startswith("@"):
                        scan_target = f"https://t.me/{url.lstrip('@')}"
                    elif ("t.me/" in url or "telegram.me/" in url) and not url.startswith(("http://", "https://")):
                        scan_target = f"https://{url}"

                    if c.blacklist.exists(scan_target):
                        any_bad = True
                        await _safe_delete(message)
                        await _safe_delete(wait)
                        await bot.send_message(
                            message.chat.id, formatters.blacklisted_link_warning(mention),
                            parse_mode="HTML",
                        )
                        await _save_forensics_case(message, "link", f"Qora ro'yxatdagi xavfli link yubordi: {url}", c)
                        await c.moderator.warn_or_ban(message.chat.id, sender_id, sender, "Qora ro'yxatdagi link")
                        break

                    result = await c.scanner.scan_url(sender_id, scan_target)
                    if result.verdict.is_bad:
                        any_bad = True
                        await _safe_delete(message)
                        await _safe_delete(wait)
                        await bot.send_message(
                            message.chat.id, formatters.dangerous_link_warning(result, mention),
                            parse_mode="HTML",
                        )
                        await _save_forensics_case(message, "link", f"Antivirus xavfli deb topgan link yubordi: {url} ({result.malicious} ta tahdid)", c)
                        await c.moderator.warn_or_ban(message.chat.id, sender_id, sender, "Xavfli link yuborish")
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
            
            if qr_data.startswith(("http://", "https://")):
                if not filters.get("filter_links", True):
                    return
                
                if c.blacklist.exists(qr_data):
                    await _safe_delete(message)
                    await bot.send_message(
                        chat_id,
                        f"🚨 <b>XAVFLI QR-KOD BLOKLANDI!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 Yuboruvchi: {mention}\n"
                        f"🔗 Havola: {qr_data[:50]}...\n"
                        f"📋 Qora ro'yxatda mavjud!",
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, "link", f"QR-kod orqali qora ro'yxatdagi xavfli link yubordi: {qr_data}", c)
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, "QR-kod orqali xavfli link tarqatish")
                    return
                
                result = await c.scanner.scan_url(sender_id, qr_data)
                if result.verdict.is_bad:
                    await _safe_delete(message)
                    await bot.send_message(
                        chat_id,
                        f"🚨 <b>XAVFLI QR-KOD BLOKLANDI!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 Yuboruvchi: {mention}\n"
                        f"🔗 Havola: {qr_data[:50]}...\n\n"
                        f"{formatters.scan_result(result)}",
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, "link", f"QR-kod orqali antivirus aniqlagan xavfli link yubordi: {qr_data} ({result.malicious} ta tahdid)", c)
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, "QR-kod orqali xavfli link tarqatish")
                else:
                    await message.reply(
                        f"🔍 <b>Rasmdan QR-kod aniqlandi!</b>\n"
                        f"🔗 Havola: <code>{qr_data}</code>\n"
                        f"✅ Havola xavfsiz topildi.",
                        parse_mode="HTML"
                    )
            else:
                if not filters.get("filter_nlp", True):
                    return
                
                nlp_res = await c.nlp.analyze_text(qr_data)
                if nlp_res["is_violation"]:
                    await _safe_delete(message)
                    category = nlp_res["category"] or "other"
                    reason = nlp_res["reason"]
                    
                    await bot.send_message(
                        chat_id,
                        f"🚨 <b>TAQIQLANGAN QR-KOD BLOKLANDI!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 Yuboruvchi: {mention}\n"
                        f"📂 Kategoriya: <code>{category.upper()}</code>\n"
                        f"📝 Izoh: <i>{reason}</i>",
                        parse_mode="HTML"
                    )
                    await _save_forensics_case(message, category, f"QR-kod matnidan qoidabuzarlik topildi: {qr_data[:100]}", c)
                    
                    reason_map = {
                        "extremism": "QR-kod orqali diniy extremism/radikalizm",
                        "drugs": "QR-kod orqali giyohvandlik targ'iboti",
                        "bullying": "QR-kod orqali kiberbulling/haqorat"
                    }
                    await c.moderator.warn_or_ban(chat_id, sender_id, sender, reason_map.get(category, f"QR-kod qoidabuzarligi: {reason}"))
                else:
                    await message.reply(
                        f"🔍 <b>Rasmdan QR-kod aniqlandi!</b>\n"
                        f"📝 Matn: <code>{qr_data}</code>\n"
                        f"✅ Matn xavfsiz topildi.",
                        parse_mode="HTML"
                    )
                    
        except Exception as e:
            logger.error("Guruh rasm/QR xato: %s", e)

    async def cmd_settings(message: Message):
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        chat_id = message.chat.id
        chat_title = message.chat.title or "Guruh"
        filters = c.user_settings.get_group_settings(chat_id)
        await message.answer(
            formatters.group_settings_text(chat_title, filters),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(chat_id, filters)
        )

    async def cmd_getlink(message: Message):
        """Guruh invite linkini yaratib bazaga saqlaydi."""
        if not await is_chat_admin(message):
            await message.answer(GROUP_ADMIN_ONLY)
            return
        chat_id = message.chat.id
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
                await message.answer(
                    f"✅ <b>Invite link saqlandi!</b>\n\n"
                    f"🔗 {invite_link}\n\n"
                    f"<i>Endi «Guruhlarim» bo'limida guruh nomiga bosib kirish mumkin.</i>",
                    parse_mode="HTML"
                )
            else:
                await message.answer("❌ Invite link yaratib bo'lmadi. Bot admin ekanligini tekshiring!")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

    async def handle_toggle_gset(call: CallbackQuery):
        chat_id = call.message.chat.id
        try:
            member = await bot.get_chat_member(chat_id, call.from_user.id)
            if member.status not in ("administrator", "creator") and call.from_user.id != settings.admin_id:
                await call.answer("Bu tugmani faqat guruh adminlari bosa oladi!", show_alert=True)
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
        chat_title = call.message.chat.title or "Guruh"
        
        await call.message.edit_text(
            formatters.group_settings_text(chat_title, updated_filters),
            parse_mode="HTML",
            reply_markup=keyboards.group_settings_kb(target_chat_id, updated_filters)
        )
        await call.answer("Sozlama o'zgartirildi!")

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

    dp.message.register(handle_group_document, F.document, group_filter)
    dp.message.register(handle_group_photo, F.photo, group_filter)
    dp.message.register(handle_group_message, group_filter)

    dp.callback_query.register(handle_toggle_gset, F.data.startswith("toggle_gset_"))
    dp.callback_query.register(handle_close_gset, F.data == "close_group_settings")
