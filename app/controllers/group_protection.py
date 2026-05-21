"""Group-protection handlers: join/leave, warn commands, file/link scanning."""
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, Message

from app.container import Container
from app.controllers.filters import is_chat_admin
from app.core.bot import bot
from app.core.config import settings
from app.models import ScanVerdict
from app.services import extract_links
from app.views import formatters
from app.views.texts import GROUP_ADDED, GROUP_ADMIN_ONLY

logger = logging.getLogger(__name__)


async def _safe_delete(msg: Message | None) -> None:
    if msg is None:
        return
    try:
        await msg.delete()
    except Exception:
        pass


def register(dp: Dispatcher, c: Container) -> None:
    group_filter = F.chat.type.in_({"group", "supergroup"})

    async def bot_added_to_group(update: ChatMemberUpdated):
        chat = update.chat
        new_status = update.new_chat_member.status
        if new_status in ("member", "administrator"):
            c.user_settings.set_group_mode(chat.id, True)
            c.groups.save(chat.id, chat.title or "Noma'lum", chat.username or "")
            try:
                await bot.send_message(chat.id, GROUP_ADDED, parse_mode="HTML")
            except Exception as e:
                logger.warning("Guruh xush kelibsiz xabari yuborilmadi: %s", e)
        elif new_status in ("left", "kicked"):
            c.user_settings.set_group_mode(chat.id, False)
            c.groups.deactivate(chat.id)

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

    async def handle_group_document(message: Message):
        chat_id = message.chat.id
        if not c.user_settings.get_group_mode(chat_id):
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
            info = await bot.get_file(doc.file_id)
            downloaded = await bot.download_file(info.file_path)
            file_bytes = downloaded.read()
            result = await c.scanner.scan_file(sender_id, file_bytes, file_name)

            if result.verdict.is_bad:
                mention = formatters.mention(sender_id, sender)
                await _safe_delete(message)
                await _safe_delete(wait)
                await bot.send_message(
                    chat_id, formatters.dangerous_file_warning(result, mention),
                    parse_mode="HTML",
                )
                await c.moderator.warn_or_ban(chat_id, sender_id, sender, "Xavfli fayl yuborish")
            else:
                await _safe_delete(wait)
        except Exception as e:
            logger.error("Guruh fayl xatolik: %s", e)
            await _safe_delete(wait)

    async def handle_group_message(message: Message):
        chat_id = message.chat.id
        if not c.user_settings.get_group_mode(chat_id):
            return
        text = message.text or message.caption or ""
        if not text or text.startswith("/"):
            return

        sender = message.from_user.first_name if message.from_user else "Noma'lum"
        sender_id = message.from_user.id if message.from_user else 0
        mention = formatters.mention(sender_id, sender)

        # 1. AI va NLP orqali matnli qonunbuzarliklarni tekshirish (Ekstremizm, Narkotik, Bulling)
        nlp_res = await c.nlp.analyze_text(text)
        if nlp_res["is_violation"]:
            # Qonunbuzarlik topildi — xabarni o'chirish va jazo qo'llash
            await _safe_delete(message)
            category = nlp_res["category"] or "other"
            reason = nlp_res["reason"]
            
            # Guruhga tahlil kartasini yuborish
            await bot.send_message(
                chat_id,
                formatters.nlp_violation_warning(category, reason, mention),
                parse_mode="HTML"
            )
            
            # Moderatsiya: warn yoki ban
            reason_map = {
                "extremism": "Diniy ekstremizm va radikalizm targ'iboti",
                "drugs": "Giyohvand moddalar yoki preparatlar yashirin savdosi/targ'iboti",
                "bullying": "Kiberbulling, shaxsiyatga tegish yoki zo'ravonlik tahdidi"
            }
            moderator_reason = reason_map.get(category, f"Siyosat buzilishi: {reason}")
            await c.moderator.warn_or_ban(chat_id, sender_id, sender, moderator_reason)
            return

        # 2. Xabar tarkibidagi linklarni tekshirish
        links = extract_links(message)
        if not links:
            return

        wait = await message.reply(
            "⏳ <b>Link tekshirilmoqda...</b>\n🛡 Ochishga shoshilmang!", parse_mode="HTML"
        )
        any_bad = False
        for url in links:
            try:
                if c.blacklist.exists(url):
                    any_bad = True
                    await _safe_delete(message)
                    await _safe_delete(wait)
                    await bot.send_message(
                        chat_id, formatters.blacklisted_link_warning(mention),
                        parse_mode="HTML",
                    )
                    await c.moderator.warn_or_ban(
                        chat_id, sender_id, sender, "Qora ro'yxatdagi link"
                    )
                    break

                result = await c.scanner.scan_url(sender_id, url)
                if result.verdict.is_bad:
                    any_bad = True
                    await _safe_delete(message)
                    await _safe_delete(wait)
                    await bot.send_message(
                        chat_id, formatters.dangerous_link_warning(result, mention),
                        parse_mode="HTML",
                    )
                    await c.moderator.warn_or_ban(
                        chat_id, sender_id, sender, "Xavfli link yuborish"
                    )
                    break
            except Exception as e:
                logger.error("Guruh link xatolik: %s", e)

        if not any_bad:
            await _safe_delete(wait)


    dp.my_chat_member.register(bot_added_to_group)
    dp.message.register(cmd_enable, Command("enable"), group_filter)
    dp.message.register(cmd_disable, Command("disable"), group_filter)
    dp.message.register(cmd_status, Command("status"), group_filter)
    dp.message.register(cmd_warn, Command("warn"), group_filter)
    dp.message.register(cmd_warns, Command("warns"), group_filter)
    dp.message.register(cmd_unwarn, Command("unwarn"), group_filter)

    dp.message.register(handle_group_document, F.document, group_filter)
    dp.message.register(handle_group_message, group_filter)
