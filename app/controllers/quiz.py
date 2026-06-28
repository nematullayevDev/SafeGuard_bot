"""Cybersecurity Quiz Controller — handles the cybersecurity test FSM flow."""
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from app.container import Container
from app.controllers.filters import ensure_registered
from app.states import QuizState
from app.views import formatters, keyboards

logger = logging.getLogger(__name__)

# Localized Cybersecurity questions
QUESTIONS = {
    "uz": [
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
    ],
    "uz_cyr": [
        {
            "text": "Фишинг (Phishing) ҳужуми нима ва у қандай амалга оширилади?",
            "options": [
                ("A) Интернет трафигини тезлаштирадиган махсус proxy-серверлар орқали", "A"),
                ("B) Сохта веб-сайтлар ва хабарлар ёрдамида шахсий маълумотлар ва паролларни ўғирлаш", "B"),
                ("C) Компьютер тизимидаги эски кеш ва кераксиз файлларни тозалаш", "C"),
                ("D) Телефон хотирасини вируслардан тозаловчи энг сўнгги антивирус дастури", "D")
            ],
            "correct": "B"
        },
        {
            "text": "Икки босқичли верификация (2-Factor Authentication) профилингизга қандай ёрдам беради?",
            "options": [
                ("A) Интернет орқали файл юклаш тезлигини сезиларли даражада оширади", "A"),
                ("B) Гуруҳлар ва каналлар сонини сунъий равишда кўпайтиришга хизмат қилади", "B"),
                ("C) Паролдан ташқари қўшимча тасдиқлаш коди орқали хавфсизликни кучайтиради", "C"),
                ("D) Расм ва видеоларнинг сифатини пасайтирмасдан ҳажмини сиқади", "D")
            ],
            "correct": "C"
        },
        {
            "text": "Номаълум манбалар ёки бегона гуруҳлардан келган шубҳали ҳаволаларни қандай текшириш лозим?",
            "options": [
                ("A) Профилактика учун ҳаволага дарҳол кириб, текшириб кўриш лозим", "A"),
                ("B) SafeGuard ботига юбориш ёки VirusTotal хизматидан фойдаланиш", "B"),
                ("C) Ҳаволани барча гуруҳдаги танишларга улашиб, фикрини сўраш", "C"),
                ("D) Браузер тарихини бутунлай тозалаб, кейин ҳаволани ишга тушириш", "D")
            ],
            "correct": "B"
        },
        {
            "text": "Киберхавфсизлик талабларига жавоб берадиган ҳақиқий мураккаб парол қандай бўлади?",
            "options": [
                ("A) Туғилган йилингиз ва исмингиздан тузилган содда матн (масалан: ali1998)", "A"),
                ("B) Телефон рақамингиз ёки фақат рақамлар кетма-кетлиги (масалан: 12345678)", "B"),
                ("C) Катта-кичик ҳарфлар, рақамлар ва махсус белгилар аралашган, камида 10-12 белги", "C"),
                ("D) Telegram usernameингиз билан бир хил парол ўрнатиш хавфсиз ҳисобланади", "D")
            ],
            "correct": "C"
        },
        {
            "text": "Номаълум веб-сайт ёки гуруҳдан юкланган .apk форматидаги файлни ўрнатиш қандай хавф туғдиради?",
            "options": [
                ("A) Ҳеч қандай хавф йўқ, аксинча у телефон хотирасини оптималлаштиради", "A"),
                ("B) Қурилманинг экран ёритиш имкониятларини ва батарея қувватини оширади", "B"),
                ("C) Телефонга зарарли вируслар (троянлар) тушиши ва банк маълумотлари ўғирланиши", "C"),
                ("D) Ушбу файл фақат мобил алоқа сифати ва интернет алоқасини яхшилайди", "D")
            ],
            "correct": "C"
        }
    ],
    "ru": [
        {
            "text": "Что такое фишинг (Phishing) и как он осуществляется?",
            "options": [
                ("A) Через специальные прокси-серверы, ускоряющие интернет-трафик", "A"),
                ("B) Кража личных данных и паролей с помощью поддельных сайтов и сообщений", "B"),
                ("C) Очистка старого кэша и ненужных файлов в компьютерной системе", "D"), # note correct option target is B
                ("D) Новейшая антивирусная программа, очищающая память от вирусов", "C")
            ],
            "correct": "B"
        },
        {
            "text": "Как двухфакторная аутентификация (2-Factor Authentication) помогает вашему профилю?",
            "options": [
                ("A) Значительно увеличивает скорость загрузки файлов через Интернет", "A"),
                ("B) Служит для искусственного увеличения количества групп и каналов", "B"),
                ("C) Усиливает безопасность с помощью дополнительного кода подтверждения", "C"),
                ("D) Сжимает размер изображений и видео без снижения их качества", "D")
            ],
            "correct": "C"
        },
        {
            "text": "Как следует проверять подозрительные ссылки из неизвестных источников?",
            "options": [
                ("A) Для профилактики следует немедленно перейти по ссылке", "A"),
                ("B) Отправить боту SafeGuard или использовать сервис VirusTotal", "B"),
                ("C) Поделиться ссылкой со всеми знакомыми и спросить их мнение", "C"),
                ("D) Полностью очистить историю браузера, а затем запустить", "D")
            ],
            "correct": "B"
        },
        {
            "text": "Какой пароль считается действительно сложным и надежным?",
            "options": [
                ("A) Простой текст, состоящий из вашего года рождения и имени", "A"),
                ("B) Номер телефона или просто последовательность цифр", "B"),
                ("C) Смесь заглавных и строчных букв, цифр и специальных знаков, от 10-12 символов", "C"),
                ("D) Установка пароля, совпадающего с вашим Telegram-username", "D")
            ],
            "correct": "C"
        },
        {
            "text": "Какую опасность представляет установка файла .apk из неизвестного источника?",
            "options": [
                ("A) Никакой опасности нет, наоборот, он оптимизирует систему", "A"),
                ("B) Повышает яркость экрана устройства и емкость батареи", "B"),
                ("C) Заражение телефона вирусами (троянами) и кража банковских данных", "C"),
                ("D) Этот файл только улучшает качество мобильной связи", "D")
            ],
            "correct": "C"
        }
    ],
    "en": [
        {
            "text": "What is a phishing attack and how is it carried out?",
            "options": [
                ("A) Through special proxy servers that speed up internet traffic", "A"),
                ("B) Stealing personal data and passwords using fake websites and messages", "B"),
                ("C) Cleaning old cache and unnecessary files in the system", "C"),
                ("D) The latest antivirus program that cleans phone memory from viruses", "D")
            ],
            "correct": "B"
        },
        {
            "text": "How does two-factor verification (2-Factor Authentication) protect your account?",
            "options": [
                ("A) Significantly increases the speed of file downloads over the Internet", "A"),
                ("B) Serves to artificially increase the number of groups and channels", "B"),
                ("C) Enhances security via an additional confirmation code", "C"),
                ("D) Compresses the size of images and videos without reducing quality", "D")
            ],
            "correct": "C"
        },
        {
            "text": "How should suspicious links from unknown sources or groups be verified?",
            "options": [
                ("A) For prevention, immediately click on the link to check it", "A"),
                ("B) Send it to SafeGuard bot or use the VirusTotal service", "B"),
                ("C) Share the link with all group contacts to ask for their opinion", "C"),
                ("D) Completely clear browser history, then launch the link", "D")
            ],
            "correct": "B"
        },
        {
            "text": "What constitutes a truly complex password that meets cybersecurity requirements?",
            "options": [
                ("A) A simple text consisting of your birth year and name", "A"),
                ("B) Your phone number or just a sequence of digits", "B"),
                ("C) A mix of uppercase and lowercase letters, numbers, and symbols, at least 10-12 chars", "C"),
                ("D) Setting a password that is identical to your Telegram username", "D")
            ],
            "correct": "C"
        },
        {
            "text": "What danger does installing a .apk file downloaded from an unknown source pose?",
            "options": [
                ("A) No danger at all; on the contrary, it optimizes phone memory", "A"),
                ("B) Increases device screen brightness capabilities and battery life", "B"),
                ("C) Malicious viruses (Trojans) infecting the phone and stealing banking details", "C"),
                ("D) This file only improves mobile network quality and internet connection", "D")
            ],
            "correct": "C"
        }
    ]
}


def register(dp: Dispatcher, c: Container) -> None:

    def _get_quiz_title(lang: str = "uz") -> str:
        return {
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

    async def cmd_quiz(message: Message):
        if not await ensure_registered(message, c):
            return
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        status = c.users.get_quiz_status(uid)
        quiz_passed = status.get("passed", False)
        
        await message.answer(
            _get_quiz_title(lang),
            reply_markup=keyboards.quiz_main_menu(quiz_passed, lang),
            parse_mode="HTML"
        )

    async def cb_quiz_main(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        status = c.users.get_quiz_status(uid)
        quiz_passed = status.get("passed", False)
        
        await call.message.edit_text(
            _get_quiz_title(lang),
            reply_markup=keyboards.quiz_main_menu(quiz_passed, lang),
            parse_mode="HTML"
        )
        await call.answer()

    async def start_quiz_session(call: CallbackQuery, state: FSMContext):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        
        await state.set_state(QuizState.answering)
        await state.update_data(current_q=0, score=0, lang=lang)
        
        q_idx = 0
        lang_questions = QUESTIONS.get(lang, QUESTIONS["uz"])
        q_data = lang_questions[q_idx]
        
        await call.message.edit_text(
            formatters.quiz_question_text(q_idx, q_data, lang),
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
        lang = data.get("lang", "uz")
        
        if q_idx != current_q:
            err_double = {
                "uz": "Eski savol, iltimos faqat oxirgi savolga javob bering!",
                "uz_cyr": "Эски савол, илтимос фақат охирги саволга жавоб беринг!",
                "ru": "Устаревший вопрос, пожалуйста, отвечайте только на последний вопрос!",
                "en": "Outdated question, please answer only the latest question!"
            }.get(lang, "")
            await call.answer(err_double, show_alert=True)
            return

        lang_questions = QUESTIONS.get(lang, QUESTIONS["uz"])
        correct_ans = lang_questions[q_idx]["correct"]
        if choice == correct_ans:
            score += 1
            ok_lbl = {"uz": "✅ To'g'ri javob!", "uz_cyr": "✅ Тўғри жавоб!", "ru": "✅ Правильный ответ!", "en": "✅ Correct answer!"}.get(lang, "")
            await call.answer(ok_lbl)
        else:
            fail_lbl = {
                "uz": f"❌ Noto'g'ri! To'g'ri javob: {correct_ans}",
                "uz_cyr": f"❌ Нотўғри! Тўғри жавоб: {correct_ans}",
                "ru": f"❌ Неверно! Правильный ответ: {correct_ans}",
                "en": f"❌ Incorrect! Correct answer: {correct_ans}"
            }.get(lang, "")
            await call.answer(fail_lbl)

        next_q = q_idx + 1
        if next_q < 5:
            await state.update_data(current_q=next_q, score=score)
            q_data = lang_questions[next_q]
            await call.message.edit_text(
                formatters.quiz_question_text(next_q, q_data, lang),
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
                formatters.quiz_result_text(score, passed, lang),
                reply_markup=keyboards.quiz_result_kb(lang),
                parse_mode="HTML"
            )

    async def cmd_quiz_group(message: Message):
        chat_id = message.chat.id
        g_settings = c.groups.get_custom_settings(chat_id)
        lang = g_settings.get("language", "uz")
        
        bot_info = await bot.get_me()
        
        btn_txt = {
            "uz": "🛡️ Testni Shaxsiy Chatda Boshlash",
            "uz_cyr": "🛡️ Тестни Шахсий Чатда Бошлаш",
            "ru": "🛡️ Начать Тест в Личном Чате",
            "en": "🛡️ Start Quiz in Private Chat"
        }.get(lang, "🛡️ Start")
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=btn_txt,
                url=f"https://t.me/{bot_info.username}?start=quiz"
            )]
        ])
        
        group_warn_msg = {
            "uz": "🛡️ <b>Kiber-Savodxonlik Viktorinasi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                  "Xavfsizlik nuqtai nazaridan, test savollariga guruhda javob berish imkoni yo'q.\n\n"
                  "👇 Viktorinani shaxsiy chatda boshlash va premium <b>«🛡️ Kiber-Himoyalangan»</b> nishonini olish uchun quyidagi tugmani bosing:",
            "uz_cyr": "🛡️ <b>Кибер-Саводхонлик Викторинаси</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      "Хавфсизлик нуқтаи назаридан, тест саволларига гуруҳда жавоб бериш имкони йўқ.\n\n"
                      "👇 Викторинани шахсий чатда бошлаш ва премиум <b>«🛡️ Кибер-Ҳимояланган»</b> нишонини олиш учун қуйидаги тугмани босинг:",
            "ru": "🛡️ <b>Викторина по Кибербезопасности</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                  "Из соображений безопасности отвечать на вопросы теста в группе невозможно.\n\n"
                  "👇 Нажмите кнопку ниже, чтобы начать викторину в личном чате и получить премиальный статус <b>«🛡️ Кибер-защищен»</b>:",
            "en": "🛡️ <b>Cybersecurity Quiz</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                  "For security reasons, quiz questions cannot be answered directly in the group.\n\n"
                  "👇 Press the button below to start the quiz in private chat and earn the premium <b>«🛡️ Cyber-Protected»</b> badge:"
        }.get(lang, "")
        
        await message.reply(
            group_warn_msg,
            reply_markup=kb,
            parse_mode="HTML"
        )

    dp.message.register(cmd_quiz, Command("quiz"), F.chat.type == "private")
    dp.message.register(cmd_quiz_group, Command("quiz"), F.chat.type.in_({"group", "supergroup"}))
    dp.callback_query.register(cb_quiz_main, F.data == "quiz_main")
    dp.callback_query.register(start_quiz_session, F.data == "quiz_start_session")
    dp.callback_query.register(handle_quiz_answer, F.data.startswith("quiz_ans_"), QuizState.answering)
