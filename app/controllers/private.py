"""Private-chat handlers: file scanning, URL scanning, spam detection."""
import logging

from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.container import Container
from app.controllers.filters import ensure_registered, is_owner
from app.core.bot import bot
from app.core.config import settings
from app.views import formatters
from app.views.keyboards import main_menu
from app.states.states import AssistantState
import aiohttp

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
        await message.answer(response, parse_mode="HTML")

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
            await message.answer(response, parse_mode="HTML")
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
        caption = message.caption or ""
        
        wait = await message.answer("⏳ Rasm yuklab olinmoqda va QR-kod tahlil qilinmoqda...")
        
        qr_data = None
        try:
            import io
            from app.services import decode_qr
            
            downloaded = io.BytesIO()
            await bot.download(photo.file_id, destination=downloaded)
            image_bytes = downloaded.getvalue()
            
            qr_data = decode_qr(image_bytes)
        except Exception as e:
            logger.error("Shaxsiy rasm/QR yuklab olish xato: %s", e)

        # Process QR data if found
        qr_response = ""
        if qr_data:
            qr_response = f"🔍 <b>QR-kod topildi!</b>\n📥 <b>Tarkibi:</b> <code>{qr_data}</code>\n\n"
            if qr_data.startswith(("http://", "https://")):
                if c.blacklist.exists(qr_data):
                    qr_response += (
                        "🔴 XAVFLI — Qora ro'yxatda!\n\n"
                        "❌ Bu link oldin xavfli topilgan!"
                    )
                else:
                    result = await c.scanner.scan_url(uid, qr_data)
                    qr_response += formatters.scan_result(result)
            else:
                nlp_res = await c.nlp.analyze_text(qr_data)
                qr_response += formatters.nlp_forensic_report(nlp_res, qr_data)
        else:
            qr_response = "❌ Ushbu rasmdan hech qanday QR-kod aniqlanmadi."

        # Process caption if present
        caption_response = ""
        if caption.strip():
            from app.services import extract_links
            caption_links = extract_links(message)
            
            caption_scan_results = []
            
            # 1. Scan links/handles in caption
            for url in caption_links:
                scan_target = url
                if url.startswith("@"):
                    scan_target = f"https://t.me/{url.lstrip('@')}"
                elif ("t.me/" in url or "telegram.me/" in url) and not url.startswith(("http://", "https://")):
                    scan_target = f"https://{url}"
                    
                if c.blacklist.exists(scan_target):
                    caption_scan_results.append(
                        f"🔴 <b>XAVFLI LINK (Qora ro'yxatda):</b> <code>{url}</code>\n"
                        f"❌ Bu havola oldin xavfli topilgan!"
                    )
                else:
                    res = await c.scanner.scan_url(uid, scan_target)
                    caption_scan_results.append(formatters.scan_result(res))
            
            # 2. Run NLP check on caption text
            try:
                nlp_res = await c.nlp.analyze_text(caption)
                if nlp_res["is_violation"]:
                    caption_scan_results.append(formatters.nlp_forensic_report(nlp_res, caption))
                elif not caption_links:
                    # If there are no links, and NLP is safe, show standard safe forensic report
                    caption_scan_results.append(formatters.nlp_forensic_report(nlp_res, caption))
            except Exception as e:
                logger.error("Caption NLP tahlil xato: %s", e)
                
            if caption_scan_results:
                caption_response = "\n\n📝 <b>Rasm ostidagi matn (caption) tahlili:</b>\n\n" + "\n\n".join(caption_scan_results)

        # Send final combined response
        final_response = qr_response
        if caption_response:
            final_response += caption_response
            
        try:
            await wait.delete()
        except Exception:
            pass
            
        await message.answer(final_response, parse_mode="HTML")

    async def cmd_assistant(message: Message, state: FSMContext):
        if not await ensure_registered(message, c):
            return
        await state.set_state(AssistantState.chatting)
        await message.answer(
            "🤖 <b>SafeGuard AI Maslahatchisiga xush kelibsiz!</b>\n\n"
            "Kiberxavfsizlik va O'zbekiston qonunchiligi (masalan, kiberjinoyatlar, firibgarliklar, JK 168-modda) bo'yicha istalgan savolingizni berishingiz mumkin.\n\n"
            "💬 <i>Suhbatni yakunlash va asosiy menyuga qaytish uchun <b>/exit</b> buyrug'ini yuboring.</i>",
            parse_mode="HTML"
        )

    async def cmd_exit_assistant(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state == AssistantState.chatting.state:
            await state.clear()
            await message.answer(
                "🏁 <b>Suhbat yakunlandi.</b> Asosiy menyuga qaytdingiz.\n"
                "Yana yordam kerak bo'lsa, /assistant buyrug'ini yuboring.",
                parse_mode="HTML",
                reply_markup=main_menu(is_owner(message))
            )
        else:
            await message.answer("Siz AI Maslahatchi suhbatida emassiz. /assistant orqali suhbatni boshlang.")

    async def handle_assistant_chat(message: Message, state: FSMContext):
        text = message.text or ""
        if not text:
            return
        if text.startswith("/"):
            if text == "/exit":
                await cmd_exit_assistant(message, state)
            elif text.startswith("/start"):
                await state.clear()
                name = message.from_user.first_name or "Foydalanuvchi"
                uid = message.from_user.id
                if c.users.is_registered(uid):
                    await message.answer(
                        f"🤖 <b>Asosiy menyuga qaytdingiz.</b>\n\nSuhbat yakunlandi. Yordam kerak bo'lsa, /assistant buyrug'ini yuboring.",
                        reply_markup=main_menu(is_owner(message)),
                        parse_mode="HTML",
                    )
                else:
                    from app.views.keyboards import phone_keyboard
                    from app.states.states import Registration
                    await message.answer(
                        "Ro'yxatdan o'tishingiz lozim. Iltimos raqamingizni yuboring:",
                        reply_markup=phone_keyboard(),
                    )
                    await state.set_state(Registration.waiting_phone)
            return

        wait = await message.answer("🤖 <i>Maslahatchi javob tayyorlamoqda...</i>", parse_mode="HTML")
        try:
            api_key = settings.gemini_api_key
            if not api_key:
                await wait.edit_text("❌ Tizimda Gemini API kaliti topilmadi. Keyinroq qayta urinib ko'ring.")
                return

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            prompt = (
                "Siz SafeGuard kiber-xavfsizlik tahlilchisi va AI maslahatchisisiz. "
                "Foydalanuvchining savoliga kiberxavfsizlik va O'zbekiston qonunchiligi nuqtai nazaridan batafsil, "
                "professional va tushunarli tarzda o'zbek tilida javob bering. O'zbekiston qonunlariga "
                "(masalan, JK 168-modda firibgarlik, kiberjinoyatlar, shaxsiy ma'lumotlar himoyasi) alohida urg'u bering.\n\n"
                f"Foydalanuvchi savoli: \"{text}\"\n\n"
                "Javobingiz professional, muloyim va foydali bo'lsin."
            )
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        reply_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        await wait.edit_text(reply_text, parse_mode="Markdown")
                    else:
                        await wait.edit_text("❌ Maslahatchi javob bera olmadi. API xatoligi yuz berdi.")
        except Exception as e:
            logger.error(f"AI Maslahatchi xatosi: {e}")
            await wait.edit_text("❌ Tizimda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")


    dp.message.register(cmd_assistant, Command("assistant"), F.chat.type == "private")
    dp.message.register(cmd_exit_assistant, Command("exit"), F.chat.type == "private")
    dp.message.register(handle_assistant_chat, AssistantState.chatting, F.chat.type == "private")
    dp.message.register(handle_document, F.document, F.chat.type == "private")
    dp.message.register(handle_private_photo, F.photo, F.chat.type == "private")
    dp.message.register(handle_message, F.chat.type == "private")
