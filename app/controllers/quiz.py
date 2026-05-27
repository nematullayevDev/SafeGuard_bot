"""Cybersecurity Quiz Controller — handles the cybersecurity test FSM flow in Uzbek."""
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.container import Container
from app.controllers.filters import ensure_registered
from app.states import QuizState
from app.views import formatters, keyboards

logger = logging.getLogger(__name__)

# 5 Professional Cybersecurity questions in Uzbek
QUESTIONS = [
    {
        "text": "Fishing (Phishing) hujumi nima va u qanday amalga oshiriladi?",
        "options": [
            ("A) Internet trafigini tezlashtiradigan maxsus proxy-serverlar orqali", "A"),
            ("B) Soxta veb-saytlar va xabarlar yordamida shaxsiy ma'lumotlar va parollarni o'g'irlash", "B"),
            ("C) Kompyuter tizimidagi eski kesh va keraksiz fayllarni tozalash", "C"),
            ("D) Telefon xotirasini viruslardan tozalovchi eng so'nggi antivirus dasturi", "D")
        ],
        "correct": "B"
    },
    {
        "text": "Ikki bosqichli verifikatsiya (2-Factor Authentication) profilingizga qanday yordam beradi?",
        "options": [
            ("A) Internet orqali fayl yuklash tezligini sezilarli darajada oshiradi", "A"),
            ("B) Guruhlar va kanallar sonini sun'iy ravishda ko'paytirishga xizmat qiladi", "B"),
            ("C) Paroldan tashqari qo'shimcha tasdiqlash kodi orqali xavfsizlikni kuchaytiradi", "C"),
            ("D) Rasm va videolarning sifatini pasaytirmasdan hajmini siqadi", "D")
        ],
        "correct": "C"
    },
    {
        "text": "Noma'lum manbalar yoki begona guruhlardan kelgan shubhali havolalarni qanday tekshirish lozim?",
        "options": [
            ("A) Profilaktika uchun havolaga darhol kirib, tekshirib ko'rish lozim", "A"),
            ("B) SafeGuard botiga yuborish yoki VirusTotal xizmatidan foydalanish", "B"),
            ("C) Havolani barcha guruhdagi tanishlarga ulashib, fikrini so'rash", "C"),
            ("D) Brauzer tarixini butunlay tozalab, keyin havolani ishga tushirish", "D")
        ],
        "correct": "B"
    },
    {
        "text": "Kiberxavfsizlik talablariga javob beradigan haqiqiy murakkab parol qanday bo'ladi?",
        "options": [
            ("A) Tug'ilgan yilingiz va ismingizdan tuzilgan sodda matn (masalan: ali1998)", "A"),
            ("B) Telefon raqamingiz yoki faqat raqamlar ketma-ketligi (masalan: 12345678)", "B"),
            ("C) Katta-kichik harflar, raqamlar va maxsus belgilar aralashgan, kamida 10-12 belgi", "C"),
            ("D) Telegram usernamesingiz bilan bir xil parol o'rnatish xavfsiz hisoblanadi", "D")
        ],
        "correct": "C"
    },
    {
        "text": "Noma'lum veb-sayt yoki guruhdan yuklangan .apk formatidagi faylni o'rnatish qanday xavf tug'diradi?",
        "options": [
            ("A) Hech qanday xavf yo'q, aksincha u telefon xotirasini optimallashtiradi", "A"),
            ("B) Qurilmaning ekran yoritish imkoniyatlarini va batareya quvvatini oshiradi", "B"),
            ("C) Telefonga zararli viruslar (troyanlar) tushishi va bank ma'lumotlari o'g'irlanishi", "C"),
            ("D) Ushbu fayl faqat mobil aloqa sifati va internet aloqasini yaxshilaydi", "D")
        ],
        "correct": "C"
    }
]


def register(dp: Dispatcher, c: Container) -> None:
    async def cmd_quiz(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
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

    async def cb_quiz_main(call: CallbackQuery):
        uid = call.from_user.id
        status = c.users.get_quiz_status(uid)
        quiz_passed = status.get("passed", False)
        
        await call.message.edit_text(
            "🛡️ <b>SafeGuard Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ushbu interaktiv test kiberxavfsizlik sohasidagi asosiy tushunchalarni tekshirish "
            "va oshirish uchun yaratilgan.\n\n"
            "📝 Test <b>5 ta professional savoldan</b> iborat bo'lib, o'tish uchun kamida <b>4 ta to'g'ri javob</b> topishingiz kerak.\n\n"
            "🎉 Testdan muvaffaqiyatli o'tsangiz, profilingiz yonida maxsus **`🛡️`** nishoni paydo bo'ladi!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboards.quiz_main_menu(quiz_passed),
            parse_mode="HTML"
        )
        await call.answer()

    async def start_quiz_session(call: CallbackQuery, state: FSMContext):
        await state.set_state(QuizState.answering)
        await state.update_data(current_q=0, score=0)
        
        q_idx = 0
        q_data = QUESTIONS[q_idx]
        
        await call.message.edit_text(
            formatters.quiz_question_text(q_idx, q_data),
            reply_markup=keyboards.quiz_question_kb(q_idx, q_data["options"]),
            parse_mode="HTML"
        )
        await call.answer()

    async def handle_quiz_answer(call: CallbackQuery, state: FSMContext):
        # Callback pattern: quiz_ans_{q_idx}_{choice}
        raw_data = call.data.replace("quiz_ans_", "")
        parts = raw_data.split("_")
        if len(parts) < 2:
            await call.answer()
            return
            
        try:
            q_idx = int(parts[0])
            choice = parts[1]
        except ValueError:
            await call.answer()
            return
            
        data = await state.get_data()
        current_q = data.get("current_q", 0)
        score = data.get("score", 0)
        
        if q_idx != current_q:
            # Prevent double click issues
            await call.answer("Eski savol, iltimos faqat oxirgi savolga javob bering!", show_alert=True)
            return

        # Check answer correctness
        correct_ans = QUESTIONS[q_idx]["correct"]
        if choice == correct_ans:
            score += 1
            await call.answer("✅ To'g'ri javob!")
        else:
            await call.answer(f"❌ Noto'g'ri! To'g'ri javob: {correct_ans}")

        next_q = q_idx + 1
        if next_q < 5:
            await state.update_data(current_q=next_q, score=score)
            q_data = QUESTIONS[next_q]
            await call.message.edit_text(
                formatters.quiz_question_text(next_q, q_data),
                reply_markup=keyboards.quiz_question_kb(next_q, q_data["options"]),
                parse_mode="HTML"
            )
        else:
            # End quiz
            await state.clear()
            uid = call.from_user.id
            passed = score >= 4
            c.users.save_quiz_result(uid, score, passed)
            
            await call.message.edit_text(
                formatters.quiz_result_text(score, passed),
                reply_markup=keyboards.quiz_result_kb(),
                parse_mode="HTML"
            )

    async def cmd_quiz_group(message: Message):
        from app.core.bot import bot
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        bot_info = await bot.get_me()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🛡️ Testni Shaxsiy Chatda Boshlash",
                url=f"https://t.me/{bot_info.username}?start=quiz"
            )]
        ])
        await message.reply(
            "🛡️ <b>Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Xavfsizlik nuqtai nazaridan, test savollariga guruhda javob berish imkoni yo'q.\n\n"
            "👇 Viktorinani shaxsiy chatda boshlash va premium <b>«🛡️ Kiber-Himoyalangan»</b> nishonini olish uchun quyidagi tugmani bosing:",
            reply_markup=kb,
            parse_mode="HTML"
        )

    dp.message.register(cmd_quiz, Command("quiz"), F.chat.type == "private")
    dp.message.register(cmd_quiz_group, Command("quiz"), F.chat.type.in_({"group", "supergroup"}))
    dp.callback_query.register(cb_quiz_main, F.data == "quiz_main")
    dp.callback_query.register(start_quiz_session, F.data == "quiz_start_session")
    dp.callback_query.register(handle_quiz_answer, F.data.startswith("quiz_ans_"), QuizState.answering)

