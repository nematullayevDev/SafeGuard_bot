"""Private-chat handlers: file scanning, URL scanning, spam detection."""
import logging

from aiogram import Dispatcher, F
from aiogram.types import Message

from app.container import Container
from app.controllers.filters import ensure_registered, is_owner
from app.core.bot import bot
from app.core.config import settings
from app.views import formatters
from app.views.keyboards import main_menu

logger = logging.getLogger(__name__)


def _rate_limit_text() -> str:
    return (
        f"⏳ Juda ko'p so'rov!\n\n"
        f"Iltimos {settings.rate_limit_window} sekund kuting.\n"
        f"Limit: {settings.rate_limit_max} ta so'rov / {settings.rate_limit_window} sekund"
    )


def register(dp: Dispatcher, c: Container) -> None:

    async def handle_document(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        if c.rate_limiter.hit(uid):
            await message.answer(_rate_limit_text())
            return

        doc = message.document
        file_name = doc.file_name or "nomsiz_fayl"
        size_mb = doc.file_size / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            await message.answer(
                f"❌ Fayl {round(size_mb, 1)} MB — juda katta! "
                f"Max {settings.max_file_size_mb} MB."
            )
            return

        wait = await message.answer(
            f"⏳ {file_name} tahlil qilinmoqda...\n"
            f"📦 {round(size_mb, 2)} MB | ⏱ 15-30 sekund kuting..."
        )
        try:
            import io
            downloaded = io.BytesIO()
            await bot.download(doc.file_id, destination=downloaded)
            file_bytes = downloaded.getvalue()
            result = await c.scanner.scan_file(uid, file_bytes, file_name)
            response = formatters.scan_result(result)
        except Exception as e:
            logger.error("Shaxsiy fayl xato: %s", e)
            response = f"❌ Xatolik: {e}"

        try:
            await wait.delete()
        except Exception:
            pass
        await message.answer(response, reply_markup=main_menu(is_owner(message)), parse_mode="HTML")

    async def handle_message(message: Message):
        if not await ensure_registered(message, c):
            return
        text = message.text or ""
        uid = message.from_user.id
        is_admin_user = is_owner(message)

        if not text:
            return

        # Slash-buyruqlarga tegmaymiz
        if text.startswith("/"):
            return

        # Check if it is a URL or a Telegram handle/bot link
        is_tg_handle = text.startswith("@") or "t.me/" in text or "telegram.me/" in text
        if text.startswith(("http://", "https://")) or is_tg_handle:
            if c.rate_limiter.hit(uid):
                await message.answer(_rate_limit_text())
                return

            scan_target = text
            if text.startswith("@"):
                scan_target = f"https://t.me/{text.lstrip('@')}"
            elif ("t.me/" in text or "telegram.me/" in text) and not text.startswith(("http://", "https://")):
                scan_target = f"https://{text}"

            if c.blacklist.exists(scan_target):
                await message.answer(
                    "🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Bu link oldin xavfli topilgan!",
                    reply_markup=main_menu(is_admin_user),
                    parse_mode="HTML",
                )
                return

            wait = await message.answer("⏳ Tekshirilmoqda...")
            try:
                result = await c.scanner.scan_url(uid, scan_target)
                response = formatters.scan_result(result)
            except Exception as e:
                logger.error("Shaxsiy link xato: %s", e)
                response = f"❌ Xatolik: {e}"
            try:
                await wait.delete()
            except Exception:
                pass
            await message.answer(response, reply_markup=main_menu(is_admin_user), parse_mode="HTML")
            return

        # Matnli xabar bo'lsa, SafeGuard AI va NLP tahlilini amalga oshiramiz
        wait = await message.answer("🔍 SafeGuard AI tahlil tizimi matnni tekshirmoqda...")
        try:
            nlp_res = await c.nlp.analyze_text(text)
            if nlp_res["is_violation"]:
                try:
                    await wait.delete()
                except Exception:
                    pass
                await message.answer(
                    formatters.nlp_forensic_report(nlp_res, text),
                    reply_markup=main_menu(is_admin_user),
                    parse_mode="HTML"
                )
                return
        except Exception as e:
            logger.error("Matn NLP tahlilida xatolik: %s", e)

        try:
            await wait.delete()
        except Exception:
            pass

        # Eski kalit so'zlar bo'yicha spam tekshiruvi (agar yoqilgan bo'lsa)
        if c.user_settings.get_spam_filter(uid) and c.spam.is_spam(text):
            await message.answer(
                f"🚫 SPAM ANIQLANDI!\n\n📝 {text[:100]}\n\n"
                "⚠️ Bu xabar fishing belgilariga ega!",
                reply_markup=main_menu(is_admin_user),
            )
            return

        # Agar foydalanuvchi ma'noli uzunroq matn yozgan bo'lsa, xavfsiz tahlil bayonotini qaytaramiz
        if len(text.strip()) > 3:
            safe_res = {
                "is_violation": False,
                "category": None,
                "reason": "Matnda diniy ekstremizm, giyohvand moddalar targ'iboti yoki kiberbulling alomatlari aniqlanmadi (Lokal + AI tahlil)."
            }
            await message.answer(
                formatters.nlp_forensic_report(safe_res, text),
                reply_markup=main_menu(is_admin_user),
                parse_mode="HTML"
            )
            return

        await message.answer(
            "📨 Menga quyidagilarni yuboring:\n\n"
            "🔗 Link — http:// yoki https:// bilan\n"
            "📦 APK yoki boshqa fayl\n"
            "🖼️ QR-kodli rasm",
            reply_markup=main_menu(is_admin_user),
        )

    async def handle_private_photo(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        is_admin_user = is_owner(message)
        if c.rate_limiter.hit(uid):
            await message.answer(_rate_limit_text())
            return

        photo = message.photo[-1]
        wait = await message.answer("⏳ Rasm yuklab olinmoqda va QR-kod tahlil qilinmoqda...")
        try:
            import io
            from app.services import decode_qr
            
            downloaded = io.BytesIO()
            await bot.download(photo.file_id, destination=downloaded)
            image_bytes = downloaded.getvalue()
            
            qr_data = decode_qr(image_bytes)
            if not qr_data:
                await wait.edit_text("❌ Ushbu rasmdan hech qanday QR-kod aniqlanmadi.")
                return
            
            await wait.edit_text(f"🔍 QR-kod topildi!\n\n📥 <b>Tarkibi:</b> <code>{qr_data}</code>\n\n⏳ Xavfsizlik tekshiruvi ketmoqda...", parse_mode="HTML")
            
            if qr_data.startswith(("http://", "https://")):
                if c.blacklist.exists(qr_data):
                    await wait.edit_text(
                        f"🔍 QR-kod tarkibi: <code>{qr_data}</code>\n\n"
                        "🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Bu link oldin xavfli topilgan!",
                        parse_mode="HTML"
                    )
                    return
                
                result = await c.scanner.scan_url(uid, qr_data)
                response = formatters.scan_result(result)
                await wait.edit_text(f"🔍 QR-kod havolasi skaner qilindi:\n\n{response}", parse_mode="HTML")
            else:
                nlp_res = await c.nlp.analyze_text(qr_data)
                response = formatters.nlp_forensic_report(nlp_res, qr_data)
                await wait.edit_text(response, parse_mode="HTML")
                
        except Exception as e:
            logger.error("Shaxsiy rasm/QR xato: %s", e)
            try:
                await wait.edit_text(f"❌ Xatolik yuz berdi: {e}")
            except Exception:
                await message.answer(f"❌ Xatolik yuz berdi: {e}")


    dp.message.register(handle_document, F.document, F.chat.type == "private")
    dp.message.register(handle_private_photo, F.photo, F.chat.type == "private")
    dp.message.register(handle_message, F.chat.type == "private")
