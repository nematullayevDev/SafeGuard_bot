"""Private-chat handlers: file scanning, URL scanning, spam detection."""
import logging
import asyncio
import re

from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.container import Container
from app.controllers.filters import ensure_registered, is_owner
from app.core.bot import bot
from app.core.config import settings
from app.views import formatters
from app.views.keyboards import main_menu
from app.states.states import AssistantState
from app.views.texts import get_text
from app.core.gemini import call_gemini_api

logger = logging.getLogger(__name__)


def _rate_limit_text(lang: str = "uz") -> str:
    return {
        "uz": (
            f"⏳ Juda ko'p so'rov!\n\n"
            f"Iltimos {settings.rate_limit_window} soniya kuting.\n"
            f"Limit: {settings.rate_limit_max} ta so'rov / {settings.rate_limit_window} soniya"
        ),
        "uz_cyr": (
            f"⏳ Жуда кўп сўров!\n\n"
            f"Илтимос {settings.rate_limit_window} сония кутинг.\n"
            f"Лимит: {settings.rate_limit_max} та сўров / {settings.rate_limit_window} сония"
        ),
        "ru": (
            f"⏳ Слишком много запросов!\n\n"
            f"Пожалуйста, подождите {settings.rate_limit_window} секунд.\n"
            f"Лимит: {settings.rate_limit_max} запросов / {settings.rate_limit_window} секунд"
        ),
        "en": (
            f"⏳ Too many requests!\n\n"
            f"Please wait {settings.rate_limit_window} seconds.\n"
            f"Limit: {settings.rate_limit_max} requests / {settings.rate_limit_window} seconds"
        )
    }.get(lang, "")


def register(dp: Dispatcher, c: Container) -> None:

    async def handle_document(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        
        if c.rate_limiter.hit(uid):
            await message.answer(_rate_limit_text(lang))
            return

        doc = message.document
        file_name = doc.file_name or "nomsiz_fayl"
        size_mb = doc.file_size / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            err_size = {
                "uz": f"❌ Fayl {round(size_mb, 1)} MB — juda katta! Max {settings.max_file_size_mb} MB.",
                "uz_cyr": f"❌ Файл {round(size_mb, 1)} MB — жуда катта! Max {settings.max_file_size_mb} MB.",
                "ru": f"❌ Файл {round(size_mb, 1)} МБ — слишком большой! Максимум {settings.max_file_size_mb} МБ.",
                "en": f"❌ File {round(size_mb, 1)} MB — too large! Max {settings.max_file_size_mb} MB."
            }.get(lang, "")
            await message.answer(err_size)
            return

        wait_text = {
            "uz": f"⏳ <b>{file_name}</b> tahlil qilinmoqda...\n📦 {round(size_mb, 2)} MB | ⏱ 15-30 soniya kuting...",
            "uz_cyr": f"⏳ <b>{file_name}</b> таҳлил қилинмоқда...\n📦 {round(size_mb, 2)} MB | ⏱ 15-30 сония кутинг...",
            "ru": f"⏳ Анализ файла <b>{file_name}</b>...\n📦 {round(size_mb, 2)} МБ | ⏱ Подождите 15-30 секунд...",
            "en": f"⏳ Analyzing <b>{file_name}</b>...\n📦 {round(size_mb, 2)} MB | ⏱ Wait 15-30 seconds..."
        }.get(lang, "")
        
        wait = await message.answer(wait_text, parse_mode="HTML")
        try:
            import io
            downloaded = io.BytesIO()
            await bot.download(doc.file_id, destination=downloaded)
            file_bytes = downloaded.getvalue()
            result = await c.scanner.scan_file(uid, file_bytes, file_name)
            response = formatters.scan_result(result, lang)
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
        lang = c.users.get_language(uid)
        is_admin_user = is_owner(message)

        if not text:
            return

        # Slash-buyruqlarga tegmaymiz
        if text.startswith("/"):
            return

        # Extract links from the message
        from app.services.link_extractor import extract_links
        links = extract_links(message)
        
        # If the user only sent a single link/handle (without other text)
        is_single_link = False
        if len(links) == 1:
            is_single_link = text.strip() == links[0] or (text.startswith("@") and " " not in text.strip())

        if is_single_link:
            # Standard single URL scanning flow
            scan_target = links[0]
            if text.startswith("@"):
                scan_target = f"https://t.me/{text.lstrip('@')}"
            elif ("t.me/" in text or "telegram.me/" in text) and not text.startswith(("http://", "https://")):
                scan_target = f"https://{text}"

            if c.rate_limiter.hit(uid):
                await message.answer(_rate_limit_text(lang))
                return

            if c.blacklist.exists(scan_target):
                bl_msg = {
                    "uz": "🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Bu link oldin xavfli topilgan!",
                    "uz_cyr": "🔴 ХАВФЛИ — Қора рўйхатда!\n\n❌ Бу линк олдин хавфли топилган!",
                    "ru": "🔴 ОПАСНО — В черном списке!\n\n❌ Эта ссылка ранее была признана вредоносной!",
                    "en": "🔴 DANGEROUS — In the blacklist!\n\n❌ This link was previously flagged as dangerous!"
                }.get(lang, "")
                await message.answer(bl_msg, parse_mode="HTML")
                return

            wait_lbl = {"uz": "⏳ Tekshirilmoqda...", "uz_cyr": "⏳ Текширилмоқда...", "ru": "⏳ Проверка...", "en": "⏳ Scanning..."}.get(lang, "⏳")
            wait = await message.answer(wait_lbl)
            try:
                result = await c.scanner.scan_url(uid, scan_target)
                response = formatters.scan_result(result, lang)
            except Exception as e:
                logger.error("Shaxsiy link xato: %s", e)
                response = f"❌ Xatolik: {e}"
            try:
                await wait.delete()
            except Exception:
                pass
            await message.answer(response, parse_mode="HTML")
            return

        # If there are links accompanied by text, or multiple links
        if links:
            if c.rate_limiter.hit(uid):
                await message.answer(_rate_limit_text(lang))
                return
                
            wait_lbl = {"uz": "⏳ Havolalar tekshirilmoqda...", "uz_cyr": "⏳ Ҳаволалар` tekshirilmoqda...", "ru": "⏳ Проверка ссылок...", "en": "⏳ Scanning links..."}.get(lang, "⏳")
            wait = await message.answer(wait_lbl)
            
            bad_link_found = False
            scan_responses = []
            
            for url in links:
                scan_target = url
                if url.startswith("@"):
                    scan_target = f"https://t.me/{url.lstrip('@')}"
                elif ("t.me/" in url or "telegram.me/" in url) and not url.startswith(("http://", "https://")):
                    scan_target = f"https://{url}"
                    
                if c.blacklist.exists(scan_target):
                    bad_link_found = True
                    bl_msg = {
                        "uz": f"🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Havola: <code>{url}</code> oldin xavfli topilgan!",
                        "uz_cyr": f"🔴 ХАВФЛИ — Қора рўйхатда!\n\n❌ Ҳавола: <code>{url}</code> олдин хавфли топилган!",
                        "ru": f"🔴 ОПАСНО — В черном списке!\n\n❌ Ссылка: <code>{url}</code> ранее была признана вредоносной!",
                        "en": f"🔴 DANGEROUS — In the blacklist!\n\n❌ Link: <code>{url}</code> was previously flagged as dangerous!"
                    }.get(lang, "")
                    await message.answer(bl_msg, parse_mode="HTML")
                    break
                    
                try:
                    result = await c.scanner.scan_url(uid, scan_target)
                    if result.verdict.is_bad:
                        bad_link_found = True
                        await message.answer(
                            formatters.dangerous_link_warning(result, message.from_user.first_name, lang),
                            parse_mode="HTML"
                        )
                        break
                    else:
                        scan_responses.append(formatters.scan_result(result, lang))
                except Exception as e:
                    logger.error("Link scanning error: %s", e)
                    
            try:
                await wait.delete()
            except Exception:
                pass
                
            if bad_link_found:
                return
                
            # If links are safe, but we have additional text, run NLP on text
            clean_text = text
            for url in links:
                clean_text = clean_text.replace(url, "")
            clean_text = clean_text.strip()
            
            # If clean_text has enough content, check with NLP
            if len(clean_text) > 3:
                wait_nlp = {"uz": "🔍 SafeGuard AI matn tahlilini amalga oshirmoqda...", "uz_cyr": "🔍 SafeGuard AI матн таҳлилини амалга оширмоқда...", "ru": "🔍 SafeGuard AI проводит анализ текста...", "en": "🔍 SafeGuard AI is analyzing the text..."}.get(lang, "🔍")
                wait = await message.answer(wait_nlp)
                try:
                    nlp_res = await c.nlp.analyze_text(text)
                    if nlp_res["is_violation"]:
                        try:
                            await wait.delete()
                        except Exception:
                            pass
                        await message.answer(
                            formatters.nlp_forensic_report(nlp_res, text, lang),
                            parse_mode="HTML"
                        )
                        return
                except Exception as e:
                    logger.error("NLP error: %s", e)
                try:
                    await wait.delete()
                except Exception:
                    pass
                    
            # If everything is safe, output the scan results of the links
            for resp in scan_responses:
                await message.answer(resp, parse_mode="HTML")
            return

        # Matnli xabar bo'lsa, SafeGuard AI va NLP tahlilini amalga oshiramiz
        wait_nlp = {"uz": "🔍 SafeGuard AI matn tahlilini amalga oshirmoqda...", "uz_cyr": "🔍 SafeGuard AI матн таҳлилини амалга оширмоқда...", "ru": "🔍 SafeGuard AI проводит анализ текста...", "en": "🔍 SafeGuard AI is analyzing the text..."}.get(lang, "🔍")
        wait = await message.answer(wait_nlp)
        try:
            nlp_res = await c.nlp.analyze_text(text)
            if nlp_res["is_violation"]:
                try:
                    await wait.delete()
                except Exception:
                    pass
                await message.answer(
                    formatters.nlp_forensic_report(nlp_res, text, lang),
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
            spam_detect_msg = {
                "uz": f"🚫 SPAM ANIQLANDI!\n\n📝 {text[:100]}\n\n⚠️ Bu xabar fishing belgilariga ega!",
                "uz_cyr": f"🚫 СПАМ АНИҚЛАНДИ!\n\n📝 {text[:100]}\n\n⚠️ Бу хабар фишинг белгиларига эга!",
                "ru": f"🚫 ОБНАРУЖЕН СПАМ!\n\n📝 {text[:100]}\n\n⚠️ Это сообщение содержит признаки фишинга!",
                "en": f"🚫 SPAM DETECTED!\n\n📝 {text[:100]}\n\n⚠️ This message contains phishing patterns!"
            }.get(lang, "")
            await message.answer(spam_detect_msg)
            return

        # Agar foydalanuvchi ma'noli uzunroq matn yozgan bo'lsa, xavfsiz tahlil bayonotini qaytaramiz
        if len(text.strip()) > 3:
            reason_safe = {
                "uz": "Matnda diniy ekstremizm, giyohvand moddalar targ'iboti yoki kiberbulling alomatlari aniqlanmadi (Lokal + AI tahlil).",
                "uz_cyr": "Матнда диний экстремизм, гиёҳванд моддалар тарғиботи ёки кибербуллинг аломатлари аниқланмади (Локал + АИ таҳлил).",
                "ru": "В тексте не обнаружено признаков религиозного экстремизма, пропаганды наркотиков или кибербуллинга (Локальный + ИИ анализ).",
                "en": "No signs of religious extremism, drug promotion, or cyberbullying detected in the text (Local + AI analysis)."
            }.get(lang, "")
            
            safe_res = {
                "is_violation": False,
                "category": None,
                "reason": reason_safe
            }
            await message.answer(
                formatters.nlp_forensic_report(safe_res, text, lang),
                parse_mode="HTML"
            )
            return

        prompt_send = {
            "uz": "📨 Menga quyidagilarni yuboring:\n\n🔗 Link — http:// yoki https:// bilan\n📦 APK yoki boshqa fayl\n🖼️ QR-kodli rasm",
            "uz_cyr": "📨 Менга қуйидагиларни юборинг:\n\n🔗 Линк — http:// ёки https:// билан\n📦 APK ёки бошқа файл\n🖼️ QR-кодли расм",
            "ru": "📨 Отправьте мне следующее:\n\n🔗 Ссылку — с http:// или https://\n📦 APK или другой файл\n🖼️ Изображение с QR-кодом",
            "en": "📨 Send me the following:\n\n🔗 Link — starting with http:// or https://\n📦 APK or any other file\n🖼️ QR-code image"
        }.get(lang, "")
        
        await message.answer(
            prompt_send,
            reply_markup=main_menu(is_admin_user, lang),
        )

    async def handle_private_photo(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        is_admin_user = is_owner(message)
        if c.rate_limiter.hit(uid):
            await message.answer(_rate_limit_text(lang))
            return

        photo = message.photo[-1]
        caption = message.caption or ""
        
        wait_text = {
            "uz": "⏳ Rasm yuklab olinmoqda va QR-kod tahlil qilinmoqda...",
            "uz_cyr": "⏳ Расм юклаб олинмоқда ва QR-код таҳлил қилинмоқда...",
            "ru": "⏳ Скачивание изображения и анализ QR-кода...",
            "en": "⏳ Downloading image and analyzing QR code..."
        }.get(lang, "")
        wait = await message.answer(wait_text)
        
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
            qr_response = {
                "uz": f"🔍 <b>QR-kod topildi!</b>\n📥 <b>Tarkibi:</b> <code>{qr_data}</code>\n\n",
                "uz_cyr": f"🔍 <b>QR-код топилди!</b>\n📥 <b>Таркиби:</b> <code>{qr_data}</code>\n\n",
                "ru": f"🔍 <b>Найден QR-код!</b>\n📥 <b>Содержимое:</b> <code>{qr_data}</code>\n\n",
                "en": f"🔍 <b>QR-code found!</b>\n📥 <b>Content:</b> <code>{qr_data}</code>\n\n"
            }.get(lang, "").format(qr_data=qr_data)
            
            if qr_data.startswith(("http://", "https://")):
                if c.blacklist.exists(qr_data):
                    qr_response += {
                        "uz": "🔴 XAVFLI — Qora ro'yxatda!\n\n❌ Bu link oldin xavfli topilgan!",
                        "uz_cyr": "🔴 ХАВФЛИ — Қора рўйхатда!\n\n❌ Бу линк олдин хавфли топилган!",
                        "ru": "🔴 ОПАСНО — В черном списке!\n\n❌ Эта ссылка ранее была признана вредоносной!",
                        "en": "🔴 DANGEROUS — In the blacklist!\n\n❌ This link was previously flagged as dangerous!"
                    }.get(lang, "")
                else:
                    result = await c.scanner.scan_url(uid, qr_data)
                    qr_response += formatters.scan_result(result, lang)
            else:
                nlp_res = await c.nlp.analyze_text(qr_data)
                qr_response += formatters.nlp_forensic_report(nlp_res, qr_data, lang)
        else:
            qr_response = {
                "uz": "❌ Ushbu rasmdan hech qanday QR-kod aniqlanmadi.",
                "uz_cyr": "❌ Ушбу расмдан ҳеч қандай QR-код аниқланмади.",
                "ru": "❌ На этом изображении не обнаружено QR-кодов.",
                "en": "❌ No QR-codes detected on this image."
            }.get(lang, "")

        # Process caption if present
        caption_response = ""
        if caption.strip():
            from app.services.link_extractor import extract_links
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
                    bl_lbl = {
                        "uz": f"🔴 <b>XAVFLI LINK (Qora ro'yxatda):</b> <code>{url}</code>\n❌ Bu havola oldin xavfli topilgan!",
                        "uz_cyr": f"🔴 <b>ХАВФЛИ ЛИНК (Қора рўйхатда):</b> <code>{url}</code>\n❌ Бу ҳавола олдин хавфли топилган!",
                        "ru": f"🔴 <b>ОПАСНАЯ ССЫЛКА (Черный список):</b> <code>{url}</code>\n❌ Эта ссылка ранее была признана вредоносной!",
                        "en": f"🔴 <b>DANGEROUS LINK (Blacklisted):</b> <code>{url}</code>\n❌ This link was previously flagged as dangerous!"
                    }.get(lang, "")
                    caption_scan_results.append(bl_lbl)
                else:
                    res = await c.scanner.scan_url(uid, scan_target)
                    caption_scan_results.append(formatters.scan_result(res, lang))
            
            # 2. Run NLP check on caption text
            try:
                nlp_res = await c.nlp.analyze_text(caption)
                if nlp_res["is_violation"]:
                    caption_scan_results.append(formatters.nlp_forensic_report(nlp_res, caption, lang))
                elif not caption_links:
                    caption_scan_results.append(formatters.nlp_forensic_report(nlp_res, caption, lang))
            except Exception as e:
                logger.error("Caption NLP tahlil xato: %s", e)
                
            if caption_scan_results:
                title_cap = {
                    "uz": "\n\n📝 <b>Rasm ostidagi matn (caption) tahlili:</b>\n\n",
                    "uz_cyr": "\n\n📝 <b>Расм остидаги матн (caption) таҳлили:</b>\n\n",
                    "ru": "\n\n📝 <b>Анализ подписи к изображению (caption):</b>\n\n",
                    "en": "\n\n📝 <b>Image caption analysis:</b>\n\n"
                }.get(lang, "")
                caption_response = title_cap + "\n\n".join(caption_scan_results)

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
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        
        await state.set_state(AssistantState.chatting)
        
        btn_txt = {
            "uz": "🏁 Suhbatni yakunlash",
            "uz_cyr": "🏁 Суҳбатни якунлаш",
            "ru": "🏁 Завершить беседу",
            "en": "🏁 End conversation"
        }.get(lang, "🏁 Suhbatni yakunlash")
        
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=btn_txt)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        welcome_assistant = {
            "uz": "🤖 <b>SafeGuard AI Maslahatchisiga xush kelibsiz!</b>\n\n"
                  "Kiberxavfsizlik va O'zbekiston qonunchiligi (masalan, kiberjinoyatlar, firibgarliklar, JK 168-modda) bo'yicha istalgan savolingizni berishingiz mumkin.\n\n"
                  "💬 <i>Suhbatni yakunlash va asosiy menyuga qaytish uchun pastdagi tugmani bosing yoki <b>/exit</b> buyrug'ini yuboring.</i>",
            "uz_cyr": "🤖 <b>SafeGuard AI Маслаҳатчисига хуш келибсиз!</b>\n\n"
                      "Киберхавфсизлик ва Ўзбекистон қонунчилиги (масалан, кибержиноятлар, фирибгарликлар, ЖК 168-модда) бўйича исталган саволингизни беришингиз мумкин.\n\n"
                      "💬 <i>Суҳбатни якунлаш ва асосий менюга қайтиш учун пастдаги тугмани босинг ёки <b>/exit</b> буйруғини юборинг.</i>",
            "ru": "🤖 <b>Добро пожаловать в ИИ-Консультант SafeGuard!</b>\n\n"
                  "Вы можете задать любой вопрос по кибербезопасности и законодательству Республики Узбекистан (например, о киберпреступлениях, мошенничестве, статье 168 УК).\n\n"
                  "💬 <i>Для завершения беседы и возврата в главное меню нажмите кнопку ниже или отправьте команду <b>/exit</b>.</i>",
            "en": "🤖 <b>Welcome to SafeGuard AI Consultant!</b>\n\n"
                  "You can ask any questions regarding cybersecurity and the legislation of the Republic of Uzbekistan (e.g., cybercrimes, fraud, Article 168 of the Criminal Code).\n\n"
                  "💬 <i>To end the conversation and return to the main menu, press the button below or send the <b>/exit</b> command.</i>"
        }.get(lang, "")
        
        await message.answer(
            welcome_assistant,
            parse_mode="HTML",
            reply_markup=kb
        )

    async def cb_assistant(call: CallbackQuery, state: FSMContext):
        uid = call.from_user.id
        if not c.users.is_registered(uid):
            await call.message.answer(get_text("register_first", "uz"), reply_markup=keyboards.go_start_kb("uz"))
            await call.answer()
            return
            
        lang = c.users.get_language(uid)
        await call.answer()
        await state.set_state(AssistantState.chatting)
        
        btn_txt = {
            "uz": "🏁 Suhbatni yakunlash",
            "uz_cyr": "🏁 Суҳбатни якунлаш",
            "ru": "🏁 Завершить беседу",
            "en": "🏁 End conversation"
        }.get(lang, "🏁 Suhbatni yakunlash")
        
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=btn_txt)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        welcome_assistant = {
            "uz": "🤖 <b>SafeGuard AI Maslahatchisiga xush kelibsiz!</b>\n\n"
                  "Kiberxavfsizlik va O'zbekiston qonunchiligi bo'yicha savollaringizni yozavering.\n\n"
                  "💬 <i>Suhbatni yakunlash uchun pastdagi tugmani bosing yoki <b>/exit</b> buyrug'ini yuboring.</i>",
            "uz_cyr": "🤖 <b>SafeGuard AI Маслаҳатчисига хуш келибсиз!</b>\n\n"
                      "Киберхавфсизлик ва Ўзбекистон қонунчилиги бўйича саволларингизни ёзаверинг.\n\n"
                      "💬 <i>Суҳбатни якунлаш учун пастдаги тугмани босинг ёки <b>/exit</b> буйруғини юборинг.</i>",
            "ru": "🤖 <b>Добро пожаловать в ИИ-Консультант SafeGuard!</b>\n\n"
                  "Вы можете задавать любые вопросы по кибербезопасности и законодательству Республики Узбекистан.\n\n"
                  "💬 <i>Для завершения беседы нажмите кнопку ниже или отправьте команду <b>/exit</b>.</i>",
            "en": "🤖 <b>Welcome to SafeGuard AI Consultant!</b>\n\n"
                  "Feel free to ask your questions about cybersecurity and the legislation of Uzbekistan.\n\n"
                  "💬 <i>To end the conversation, press the button below or send the <b>/exit</b> command.</i>"
        }.get(lang, "")
        
        await call.message.answer(
            welcome_assistant,
            parse_mode="HTML",
            reply_markup=kb
        )

    async def cmd_exit_assistant(message: Message, state: FSMContext):
        current_state = await state.get_state()
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        
        if current_state == AssistantState.chatting.state:
            await state.clear()
            
            close_text = {
                "uz": "🏁 <b>Suhbat yakunlandi.</b>",
                "uz_cyr": "🏁 <b>Суҳбат якунланди.</b>",
                "ru": "🏁 <b>Беседа завершена.</b>",
                "en": "🏁 <b>Conversation ended.</b>"
            }.get(lang, "")
            
            await message.answer(
                close_text,
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove()
            )
            
            name = message.from_user.first_name or "Foydalanuvchi"
            await message.answer(
                get_text("welcome", lang).format(name=name),
                parse_mode="HTML",
                reply_markup=main_menu(is_owner(message), lang)
            )
        else:
            not_in_chat = {
                "uz": "Siz AI Maslahatchi suhbatida emassiz. Bosh menyudan AI Maslahatchini tanlang.",
                "uz_cyr": "Сиз AI Маслаҳатчи суҳбатида эмассиз. Бош менюдан AI Маслаҳатчини танланг.",
                "ru": "Вы не находитесь в режиме беседы с ИИ. Выберите ИИ-Консультанта в главном меню.",
                "en": "You are not in a conversation with AI. Select AI Consultant from the main menu."
            }.get(lang, "")
            await message.answer(not_in_chat)

    async def handle_assistant_chat(message: Message, state: FSMContext):
        text = message.text or ""
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        
        if not text:
            return
            
        exit_keys = ["🏁 Suhbatni yakunlash", "🏁 Суҳбатни якунлаш", "🏁 Завершить беседу", "🏁 End conversation", "/exit"]
        if text in exit_keys:
            await cmd_exit_assistant(message, state)
            return
            
        if text.startswith("/"):
            if text.startswith("/start"):
                await state.clear()
                name = message.from_user.first_name or "Foydalanuvchi"
                close_text = {
                    "uz": "🏁 <b>Suhbat yakunlandi.</b>",
                    "uz_cyr": "🏁 <b>Суҳбат якунланди.</b>",
                    "ru": "🏁 <b>Беседа завершена.</b>",
                    "en": "🏁 <b>Conversation ended.</b>"
                }.get(lang, "")
                await message.answer(
                    close_text,
                    parse_mode="HTML",
                    reply_markup=ReplyKeyboardRemove()
                )
                await message.answer(
                    get_text("welcome", lang).format(name=name),
                    reply_markup=main_menu(is_owner(message), lang),
                    parse_mode="HTML",
                )
            return

        wait_text = {
            "uz": "🤖 <i>Maslahatchi javob tayyorlamoqda...</i>",
            "uz_cyr": "🤖 <i>Маслаҳатчи жавоб тайёрламоқда...</i>",
            "ru": "🤖 <i>Консультант готовит ответ...</i>",
            "en": "🤖 <i>Consultant is preparing an answer...</i>"
        }.get(lang, "")
        wait = await message.answer(wait_text, parse_mode="HTML")
        try:
            api_key = settings.gemini_api_key
            if not api_key:
                err_key = {
                    "uz": "❌ Tizimda Gemini API kaliti topilmadi. Keyinroq qayta urinib ko'ring.",
                    "uz_cyr": "❌ Тизимда Gemini API калити топилмади. Кейинроқ қайта уриниб кўринг.",
                    "ru": "❌ В системе не найден ключ Gemini API. Попробуйте позже.",
                    "en": "❌ Gemini API key not found in the system. Please try again later."
                }.get(lang, "")
                await wait.edit_text(err_key)
                return

            prompt_language = {
                "uz": "o'zbek tilida",
                "uz_cyr": "ўзбек тилида (кирилл алифбосида)",
                "ru": "на русском языке",
                "en": "in English"
            }.get(lang, "o'zbek tilida")
            
            laws_note = {
                "uz": "O'zbekiston Respublikasi qonunchiligi nuqtai nazaridan (JK 168-modda firibgarlik, kiberjinoyatlar, shaxsiy ma'lumotlar himoyasi)",
                "uz_cyr": "Ўзбекистон Республикаси қонунчилиги нуқтаи назаридан (ЖК 168-модда фирибгарлик, кибержиноятлар, шахсий маълумотлар ҳимояси)",
                "ru": "с точки зрения законодательства Республики Узбекистан (статья 168 УК о мошенничестве, киберпреступления, защита персональных данных)",
                "en": "from the perspective of the legislation of the Republic of Uzbekistan (Article 168 of the Criminal Code on fraud, cybercrimes, personal data protection)"
            }.get(lang, "")

            prompt = (
                f"Siz SafeGuard kiber-xavfsizlik tahlilchisi va AI maslahatchisisiz. "
                f"Foydalanuvchining savoliga kiberxavfsizlik va {laws_note} nuqtai nazaridan batafsil, "
                f"professional va tushunarli tarzda {prompt_language} javob bering.\n\n"
                f"Foydalanuvchi savoli: \"{text}\"\n\n"
                "Javobingiz professional, muloyim va foydali bo'lsin."
            )

            response_text = await call_gemini_api(api_key, prompt)
            try:
                await wait.edit_text(response_text, parse_mode="Markdown")
            except Exception as tg_err:
                logger.warning(f"Telegram Markdown parse failed: {tg_err}")
                await wait.edit_text(response_text)
        except Exception as e:
            logger.error(f"AI Maslahatchi xatosi: {e}")
            err_general = {
                "uz": f"❌ Maslahatchi javob bera olmadi. {str(e)}.",
                "uz_cyr": f"❌ Маслаҳатчи жавоб бера олмади. {str(e)}.",
                "ru": f"❌ Консультант не смог ответить. {str(e)}.",
                "en": f"❌ Consultant could not answer. {str(e)}."
            }.get(lang, "").format(e=str(e))
            await wait.edit_text(err_general)


    dp.message.register(cmd_assistant, Command("assistant"), F.chat.type == "private")
    dp.message.register(cmd_exit_assistant, Command("exit"), F.chat.type == "private")
    dp.message.register(handle_assistant_chat, AssistantState.chatting, F.chat.type == "private")
    dp.message.register(handle_document, F.document, F.chat.type == "private")
    dp.message.register(handle_private_photo, F.photo, F.chat.type == "private")
    dp.message.register(handle_message, F.chat.type == "private")
    dp.callback_query.register(cb_assistant, F.data == "ai_assistant")
