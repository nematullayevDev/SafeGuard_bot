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
            info = await bot.get_file(doc.file_id)
            downloaded = await bot.download_file(info.file_path)
            result = await c.scanner.scan_file(uid, downloaded.read(), file_name)
            response = formatters.scan_result(result)
        except Exception as e:
            logger.error("Shaxsiy fayl xato: %s", e)
            response = f"❌ Xatolik: {e}"

        try:
            await wait.delete()
        except Exception:
            pass
        await message.answer(response, reply_markup=main_menu(is_owner(message)))

    async def handle_message(message: Message):
        if not await ensure_registered(message, c):
            return
        text = message.text or ""
        uid = message.from_user.id
        is_admin_user = is_owner(message)

        if text.startswith(("http://", "https://")):
            if c.rate_limiter.hit(uid):
                await message.answer(_rate_limit_text())
                return

            if c.blacklist.exists(text):
                await message.answer(
                    "🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Bu link oldin xavfli topilgan!",
                    reply_markup=main_menu(is_admin_user),
                )
                return

            wait = await message.answer("⏳ Tekshirilmoqda...")
            try:
                result = await c.scanner.scan_url(uid, text)
                response = formatters.scan_result(result)
            except Exception as e:
                logger.error("Shaxsiy link xato: %s", e)
                response = f"❌ Xatolik: {e}"
            try:
                await wait.delete()
            except Exception:
                pass
            await message.answer(response, reply_markup=main_menu(is_admin_user))
            return

        if c.user_settings.get_spam_filter(uid) and c.spam.is_spam(text):
            await message.answer(
                f"🚫 SPAM ANIQLANDI!\n\n📝 {text[:100]}\n\n"
                "⚠️ Bu xabar fishing belgilariga ega!",
                reply_markup=main_menu(is_admin_user),
            )
            return

        await message.answer(
            "📨 Menga quyidagilarni yuboring:\n\n"
            "🔗 Link — http:// yoki https:// bilan\n"
            "📦 APK yoki boshqa fayl",
            reply_markup=main_menu(is_admin_user),
        )

    dp.message.register(handle_document, F.document, F.chat.type == "private")
    dp.message.register(handle_message, F.chat.type == "private")
