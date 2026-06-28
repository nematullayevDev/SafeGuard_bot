"""Localized static message templates."""

LOCALIZED_TEXTS = {
    "uz": {
        "welcome": (
            "🛡 <b>SafeGuard — Premium Telegram Kiber-Himoya Tizimi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Assalomu alaykum, hurmatli <b>{name}</b>!\n\n"
            "Bizning intellektual tizimimizga xush kelibsiz. Men guruhlaringiz xavfsizligi, fishing havolalar va virusli fayllardan professional darajada himoya qilish uchun yaratilganman.\n\n"
            "⚡ <b>Tizimimizning asosiy imkoniyatlari:</b>\n"
            " 🔗 <b>Kiber-Tahlil</b> — Yuborilgan har qanday havolalarni xavflilik darajasini aniqlash\n"
            " 📦 <b>Antivirus Moduli</b> — APK va boshqa virusli hujjatlarni real vaqtda bloklash\n"
            " 📷 <b>QR-kod Skaneri</b> — Rasmlardagi yashirin xavfli havola va matnlarni fosh qilish\n"
            " 🧠 <b>Intellektual Nazorat</b> — Guruhdagi matnlarni diniy ekstremizm va narkotik targ'ibotiga tahlil qilish\n"
            " 🛡 <b>Guruh Rejimi</b> — Guruh a'zolarini kiberbulling va haqoratlardan 24/7 himoyalash\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📂 <i>Tizim buyruqlari va qo'shimcha ma'lumotlar bilan tanishish uchun quyidagi menyudan foydalaning:</i> 👇"
        ),
        "reg_required": (
            "🛡 <b>SafeGuard — Premium Kiber-Himoya Tizimi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Salom, <b>{name}</b>!\n\n"
            "Xavfsizlik tizimimizdan to'liq foydalanish va shaxsingizni tasdiqlash uchun ro'yxatdan o'tishingiz so'raladi.\n\n"
            "📱 <b>Ro'yxatdan o'tish uchun:</b>\n"
            "Kiber-tizimimiz sizning telefon raqamingiz orqali verifikatsiya qiladi. Bu shaxsiy profilingiz va guruhlaringiz xavfsizligini ta'minlash uchun zarur.\n\n"
            "🇺🇿 <b>Diqqat:</b> Tizimdan foydalanish uchun <b>O'zbekiston raqami (+998)</b> talab qilinadi.\n"
            "Boshqa davlat raqami bilan ro'yxatdan o'tish mumkin emas.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <i>Davom etish uchun quyidagi <b>«📱 Raqamimni ulashish»</b> tugmasini bosing:</i>"
        ),
        "phone_not_uz": (
            "🇺🇿 <b>Faqat O'zbekiston raqami qabul qilinadi!</b>\n\n"
            "Sizning Telegram raqamingiz <b>{phone}</b> — bu O'zbekiston raqami emas.\n\n"
            "❗ Tizimdan foydalanish uchun <b>+998</b> bilan boshlangan O'zbek raqami talab qilinadi.\n\n"
            "Agar O'zbekiston raqamiga ega bo'lsangiz, Telegram profilingizni shu raqam bilan yangilang va qayta urinib ko'ring."
        ),
        "group_added": (
            "🛡 <b>SafeGuard — Intellektual Guruh Himoyasi Faollashtirildi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Assalomu alaykum, guruh a'zolari!\n\n"
            "Guruh xavfsizligi professional <b>SafeGuard Bot</b> nazorati ostiga olindi. Tizim avtomatik rejimda ishlaydi:\n\n"
            " 🚫 <b>Fishing va Spam</b> — Xavfli fayl va havolalar darhol o'chiriladi\n"
            " 📷 <b>QR-kod Himoyasi</b> — Rasmlardagi xavfli QR-kodlar skanerlanib, bloklanadi\n"
            " ⚖️ <b>Tergov va Jazolar</b> — 3 marta ogohlantirish (warn) olgan qonunbuzarlar guruhdan chetlashtiriladi (ban)\n"
            " 🟢 <b>Tinch Rejim</b> — Xavfsiz suhbatlarga tizim hech qanday xalal bermaydi\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>Adminlar uchun boshqaruv buyruqlari:</b>\n"
            " ▫️ /enable — Himoya tizimini faollashtirish\n"
            " ▫️ /disable — Himoyani vaqtincha to'xtatish\n"
            " ▫️ /status — Himoyaning joriy holati\n"
            " ▫️ /warn — Qonunbuzarga ogohlantirish berish (reply)\n"
            " ▫️ /warns — Ogohlantirishlar sonini ko'rish (reply)\n"
            " ▫️ /unwarn — Ogohlantirishlarni qaytarib olish (reply)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 <i>Tizim SafeGuard tahlil va himoya modullari asosida ishlaydi.</i>"
        ),
        "admin_only": "⛔ Bu buyruq faqat admin uchun!",
        "admin_only_alert": "⛔ Faqat admin!",
        "group_admin_only": "⛔ Bu buyruq faqat guruh adminlari uchun!",
        "register_first": (
            "⚠️ Avval ro'yxatdan o'ting!\n\n/start ni bosing.\n"
            "⚠️ Сначала зарегистрируйтесь!\n\nНажмите /start.\n"
            "⚠️ Register first!\n\nClick /start."
        ),
        "channel_subscribe_required": (
            "📢 <b>SafeGuard rasmiy kanaliga obuna bo'ling!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Hurmatli <b>{name}</b>, botdan to'liq foydalanish uchun\n"
            "rasmiy kanalimizga obuna bo'lishingiz shart.\n\n"
            "📌 Kanalda nima bor?\n"
            " 🔐 Kiberxavfsizlik yangiliklari\n"
            " ⚠️ Yangi tahdidlar haqida ogohlantirishlar\n"
            " 💡 Foydali maslahatlar va ko'rsatmalar\n"
            " 🛡 Bot yangiliklari va yeni funksiyalar\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <b>Quyidagi tugmani bosib kanalga o'ting, obuna bo'ling va «✅ Tekshirish» tugmasini bosing:</b>"
        ),
        "channel_subscribe_success": (
            "✅ <b>Rahmat! Obuna tasdiqlandi.</b>\n\n"
            "Endi botdan to'liq foydalanishingiz mumkin 🛡"
        ),
        "channel_subscribe_fail": (
            "❌ <b>Siz hali kanalga obuna bo'lmagansiz!</b>\n\n"
            "Iltimos, avval {channel} kanaliga obuna bo'ling,\n"
            "so'ng <b>«✅ Tekshirish»</b> tugmasini bosing."
        ),
        "channel_subscribe_fail_alert": (
            "❌ Siz hali kanalga obuna bo'lmagansiz!\n\n"
            "Iltimos, avval {channel} kanaliga obuna bo'ling,\n"
            "so'ng «✅ Tekshirish» tugmasini bosing."
        ),
        "group_no_invite_link": (
            "🚫 <b>SafeGuard Bot guruhga qo'shila olmadi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Guruh sozlamalarida <b>«Havola orqali taklif qilish»</b> funksiyasi <b>O'CHIRILGAN</b>.\n\n"
            "Bu funksiya o'chiq bo'lsa, SafeGuard Bot guruhni to'g'ri sozlay olmaydi va himoya funksiyalarini ishga tushira olmaydi.\n\n"
            "Shuning uchun bot guruhdan <b>avtomatik chiqib ketdi</b>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>Tuzatish uchun:</b>\n\n"
            " 1️⃣ Guruh sozlamalarini oching\n"
            " 2️⃣ <b>Guruh turi</b> bo'limiga kiring\n"
            " 3️⃣ <b>«Havola orqali taklif qilish»</b> ni yoqing ✅\n"
            " 4️⃣ Botni qayta guruhga qo'shing va <b>Admin huquqi</b> bering\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <i>SafeGuard — Faqat to'g'ri sozlangan guruhlarda ishlaydi!</i>"
        )
    },
    "uz_cyr": {
        "welcome": (
            "🛡 <b>SafeGuard — Премиум Telegram Кибер-Ҳимоя Тизими</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Ассалому алайкум, ҳурматли <b>{name}</b>!\n\n"
            "Бизнинг интеллектуал тизимимизга хуш келибсиз. Мен гуруҳларингиз хавфсизлиги, фишинг ҳаволалар ва вирусли файллардан профессионал даражада ҳимоя қилиш учун яратилганман.\n\n"
            "⚡ <b>Тизимимизнинг asosiy имкониятлари:</b>\n"
            " 🔗 <b>Кибер-Таҳлил</b> — Юборилган ҳар қандай ҳаволаларни хавфлилик даражасини аниқлаш\n"
            " 📦 <b>Антивирус Модули</b> — APK ва бошқа вирусли ҳужжатларни реал вақтда блоклаш\n"
            " 📷 <b>QR-код Сканери</b> — Расмлардаги яширин хавфли ҳавола ва матнларни фош қилиш\n"
            " 🧠 <b>Интеллектуал Назорат</b> — Гуруҳдаги матнларни диний экстремизм ва наркотик тарғиботига таҳлил қилиш\n"
            " 🛡 <b>Гуруҳ Режими</b> — Гуруҳ аъзоларини кибербуллинг ва ҳақоратлардан 24/7 ҳимоялаш\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📂 <i>Тизим буйруқлари ва қўшимча маълумотлар билан танишиш учун қуйидаги менюдан фойдаланинг:</i> 👇"
        ),
        "reg_required": (
            "🛡 <b>SafeGuard — Премиум Кибер-Ҳимоя Тизими</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Салом, <b>{name}</b>!\n\n"
            "Хавфсизлик тизимимиздан тўлиқ фойдаланиш ва шахсингизни тасдиқлаш учун рўйхатдан ўтишингиз сўралади.\n\n"
            "📱 <b>Рўйхатдан ўтиш учун:</b>\n"
            "Кибер-тизимимиз сизнинг телефон рақамингиз орқали верификация қилади. Бу шахсий профилингиз ва гуруҳларингиз хавфсизлигини таъминлаш учун зарур.\n\n"
            "🇺🇿 <b>Диққат:</b> Тизимдан фойдаланиш учун <b>Ўзбекистон рақами (+998)</b> талаб қилинади.\n"
            "Бошқа давлат рақами билан рўйхатдан ўтиш мумкин эмас.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <i>Давом этиш учун қуйидаги <b>«📱 Рақамимни улашиш»</b> тугмасини босинг:</i>"
        ),
        "phone_not_uz": (
            "🇺🇿 <b>Фақат Ўзбекистон рақами қабул қилинади!</b>\n\n"
            "Сизнинг Telegram рақамингиз <b>{phone}</b> — бу Ўзбекистон рақами эмас.\n\n"
            "❗ Тизимдан фойдаланиш учун <b>+998</b> билан бошланган Ўзбек рақами талаб қилинади.\n\n"
            "Агар Ўзбекистон рақамига эга бўлсангиз, Telegram профилингизни шу рақам билан янгиланг ва қайта уриниб кўринг."
        ),
        "group_added": (
            "🛡 <b>SafeGuard — Интеллектуал Гуруҳ Ҳимояси Фаоллаштирилди!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Ассалому алайкум, гуруҳ аъзолари!\n\n"
            "Гуруҳ хавфсизлиги профессионал <b>SafeGuard Bot</b> назорати остига олинди. Тизим автоматик режимда ишлайди:\n\n"
            " 🚫 <b>Фишинг ва Спам</b> — Хавфли файл ва ҳаволалар дарҳол ўчирилади\n"
            " 📷 <b>QR-код Ҳимояси</b> — Расмлардаги хавфли QR-кодлар сканерланиб, блокланади\n"
            " ⚖️ <b>Таргов ва Жазолар</b> — 3 марта огоҳлантириш (warn) олган қонунбузарлар гуруҳдан четлаштирилади (ban)\n"
            " 🟢 <b>Тинч Режим</b> — Хавфсиз суҳбатларга тизим ҳеч қандай халал бермайди\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>Админлар учун бошқарув буйруқлари:</b>\n"
            " ▫️ /enable — Ҳимоя тизимини фаоллаштириш\n"
            " ▫️ /disable — Ҳимояни вақтинча тўхтатиш\n"
            " ▫️ /status — Ҳимоянинг жорий ҳолати\n"
            " ▫️ /warn — Қонунбузарга огоҳлантириш бериш (reply)\n"
            " ▫️ /warns — Огоҳлантиришлар сонини кўриш (reply)\n"
            " ▫️ /unwarn — Огоҳлантиришларни қайтариб олиш (reply)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 <i>Тизим SafeGuard таҳлил ва ҳимоя модуллари асосида ишлайди.</i>"
        ),
        "admin_only": "⛔ Бу буйруқ фақат админ учун!",
        "admin_only_alert": "⛔ Фақат админ!",
        "group_admin_only": "⛔ Бу буйруқ фақат гуруҳ админлари учун!",
        "register_first": (
            "⚠️ Аввал рўйхатdan ўтинг! /start ни босинг.\n"
            "⚠️ Сначала зарегистрируйтесь! Нажмите /start.\n"
            "⚠️ Register first! Click /start."
        ),
        "channel_subscribe_required": (
            "📢 <b>SafeGuard расмий каналига обуна бўлинг!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Ҳурматли <b>{name}</b>, ботдан тўлиқ фойдаланиш учун\n"
            "расмий каналимизга обуна бўлишингиз шаart.\n\n"
            "📌 Каналда нима бор?\n"
            " 🔐 Киберхавфсизлик янгиликлари\n"
            " ⚠️ Янги таҳдидлар ҳақида огоҳлантиришлар\n"
            " 💡 Фойдали маслаҳатлар ва кўрсатмалар\n"
            " 🛡 Бот янгиликлари ва янги функциялар\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <b>Қуйидаги тугмани босиб каналга ўтинг, обуна бўлинг ва «✅ Текшириш» тугмасини босинг:</b>"
        ),
        "channel_subscribe_success": (
            "✅ <b>Раҳмат! Обуна тасдиқланди.</b>\n\n"
            "Энди ботдан тўлиқ фойдаланишингиз мумкин 🛡"
        ),
        "channel_subscribe_fail": (
            "❌ <b>Сиз ҳали каналга обуна бўлмагансиз!</b>\n\n"
            "Илтимос, аввал {channel} каналига обуна бўлинг,\n"
            "сўнг <b>«✅ Текшириш»</b> тугмасини босинг."
        ),
        "channel_subscribe_fail_alert": (
            "❌ Сиз ҳали каналга обуна бўлмагансиз!\n\n"
            "Илтимос, аввал {channel} каналига обуна бўлинг,\n"
            "сўнг «✅ Текшириш» тугмасини босинг."
        ),
        "group_no_invite_link": (
            "🚫 <b>SafeGuard Bot гуруҳга қўшила олмади!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Гуруҳ созламаларида <b>«Ҳавола орқали таклиф қилиш»</b> функцияси <b>ЎЧИРИЛГАН</b>.\n\n"
            "Бу функция ўчиқ бўлса, SafeGuard Bot гуруҳни тўғри созлай олмайди ва ҳимоя функцияларини ишга тушира олмайди.\n\n"
            "Шунинг учун бот гуруҳдан <b>автоматик чиқиб кетди</b>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>Тузатиш учун:</b>\n\n"
            " 1️⃣ Гуруҳ созламаларини очинг\n"
            " 2️⃣ <b>Гуруҳ тури</b> бўлимига киринг\n"
            " 3️⃣ <b>«Ҳавола орқали таклиф қилиш»</b> ни ёқинг ✅\n"
            " 4️⃣ Ботни қайта гуруҳга қўшинг ва <b>Админ ҳуқуқи</b> беринг\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <i>SafeGuard — Фақат тўғри созланган гуруҳларда ишлайди!</i>"
        )
    },
    "ru": {
        "welcome": (
            "🛡 <b>SafeGuard — Premium Система Кибербезопасности Telegram</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Здравствуйте, уважаемый <b>{name}</b>!\n\n"
            "Добро пожаловать в нашу интеллектуальную систему. Я разработан для защиты ваших групп, обнаружения фишинговых ссылок и вредоносных файлов на профессиональном уровне.\n\n"
            "⚡ <b>Основные возможности нашей системы:</b>\n"
            " 🔗 <b>Кибер-анализ</b> — Определение уровня угрозы для любой отправленной ссылки\n"
            " 📦 <b>Модуль антивируса</b> — Блокировка APK и других опасных документов в реальном времени\n"
            " 📷 <b>Сканер QR-кодов</b> — Разоблачение скрытых ссылок и текстов в изображениях\n"
            " 🧠 <b>Интеллектуальный контроль</b> — Анализ текстов на пропаганду наркотиков и экстремизма\n"
            " 🛡 <b>Режим групп</b> — Защита участников группы от кибербуллинга и оскорблений 24/7\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📂 <i>Используйте меню ниже для ознакомления с командами и дополнительной информацией:</i> 👇"
        ),
        "reg_required": (
            "🛡 <b>SafeGuard — Premium Система Киберзащиты</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Привет, <b>{name}</b>!\n\n"
            "Для полного доступа к нашей системе безопасности и верификации вашего профиля просим вас пройти регистрацию.\n\n"
            "📱 <b>Для регистрации:</b>\n"
            "Наша кибер-система проверяет профиль с помощью номера телефона. Это необходимо для обеспечения безопасности вашего профиля и ваших групп.\n\n"
            "🇺🇿 <b>Внимание:</b> Для использования системы требуется <b>номер Узбекистана (+998)</b>.\n"
            "Регистрация с номерами других стран невозможна.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <i>Для продолжения нажмите кнопку <b>«📱 Поделиться контактом»</b> ниже:</i>"
        ),
        "phone_not_uz": (
            "🇺🇿 <b>Принимаются только номера Узбекистана!</b>\n\n"
            "Ваш номер Telegram <b>{phone}</b> не является узбекским.\n\n"
            "❗ Для использования системы необходим узбекский номер, начинающийся с <b>+998</b>.\n\n"
            "Если у вас есть номер Узбекистана, пожалуйста, обновите ваш профиль Telegram с этим номером и попробуйте снова."
        ),
        "group_added": (
            "🛡 <b>SafeGuard — Интеллектуальная защита группы активирована!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Приветствуем участников группы!\n\n"
            "Безопасность группы взята под профессиональный контроль <b>SafeGuard Bot</b>. Система работает в автоматическом режиме:\n\n"
            " 🚫 <b>Фишинг и Спам</b> — Опасные файлы и ссылки удаляются мгновенно\n"
            " 📷 <b>Защита QR-кодов</b> — Опасные QR-коды на изображениях сканируются и блокируются\n"
            " ⚖️ <b>Наказания</b> — Нарушители, получившие 3 предупреждения (warn), будут забанены\n"
            " 🟢 <b>Тихий режим</b> — Система не мешает безопасным беседам\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>Команды управления для администраторов:</b>\n"
            " ▫️ /enable — Активировать систему защиты\n"
            " ▫️ /disable — Временно приостановить защиту\n"
            " ▫️ /status — Текущий статус защиты\n"
            " ▫️ /warn — Выдать предупреждение нарушителю (reply)\n"
            " ▫️ /warns — Посмотреть количество предупреждений (reply)\n"
            " ▫️ /unwarn — Снять предупреждения (reply)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 <i>Система работает на базе модулей анализа и защиты SafeGuard.</i>"
        ),
        "admin_only": "⛔ Эта команда доступна только владельцу бота!",
        "admin_only_alert": "⛔ Только для администраторов!",
        "group_admin_only": "⛔ Эта команда доступна только администраторам группы!",
        "register_first": (
            "⚠️ Сначала зарегистрируйтесь!\n\nНажмите /start."
        ),
        "channel_subscribe_required": (
            "📢 <b>Подпишитесь на официальный канал SafeGuard!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Уважаемый <b>{name}</b>, для полноценного использования бота\n"
            "вам необходимо подписаться на наш официальный канал.\n\n"
            "📌 Что публикуется на канале?\n"
            " 🔐 Новости кибербезопасности\n"
            " ⚠️ Предупреждения о новых угрозах\n"
            " 💡 Полезные советы и инструкции\n"
            " 🛡 Обновления и новые функции бота\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <b>Перейдите по кнопке ниже, подпишитесь на канал и нажмите «✅ Проверить»:</b>"
        ),
        "channel_subscribe_success": (
            "✅ <b>Спасибо! Подписка подтверждена.</b>\n\n"
            "Теперь вы можете полноценно использовать бота 🛡"
        ),
        "channel_subscribe_fail": (
            "❌ <b>Вы еще не подписались на канал!</b>\n\n"
            "Пожалуйста, сначала подпишитесь на канал {channel},\n"
            "затем нажмите кнопку <b>«✅ Проверить»</b>."
        ),
        "channel_subscribe_fail_alert": (
            "❌ Вы еще не подписались на канал!\n\n"
            "Пожалуйста, сначала подпишитесь на канал {channel},\n"
            "затем нажмите кнопку «✅ Проверить»."
        ),
        "group_no_invite_link": (
            "🚫 <b>SafeGuard Bot не смог присоединиться к группе!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ В настройках группы <b>ОТКЛЮЧЕНА</b> функция <b>«Приглашение по ссылке»</b>.\n\n"
            "Без этой функции SafeGuard Bot не может корректно настроить и активировать функции защиты.\n\n"
            "Поэтому бот <b>автоматически покинул группу</b>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>Для исправления:</b>\n\n"
            " 1️⃣ Откройте настройки группы\n"
            " 2️⃣ Перейдите в раздел <b>Тип группы</b>\n"
            " 3️⃣ Включите <b>«Приглашение по ссылке»</b> ✅\n"
            " 4️⃣ Снова добавьте бота в группу и дайте права <b>Администратора</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <i>SafeGuard работает только в правильно настроенных группах!</i>"
        )
    },
    "en": {
        "welcome": (
            "🛡 <b>SafeGuard — Premium Telegram Cyber-Security System</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Hello, dear <b>{name}</b>!\n\n"
            "Welcome to our intelligent system. I am designed to protect your groups and defend against phishing links and malicious files at a professional level.\n\n"
            "⚡ <b>Key features of our system:</b>\n"
            " 🔗 <b>Cyber-Analysis</b> — Detect the threat level of any sent link\n"
            " 📦 <b>Antivirus Module</b> — Block APKs and other malicious documents in real time\n"
            " 📷 <b>QR-code Scanner</b> — Reveal hidden links and texts in images\n"
            " 🧠 <b>Intellectual Control</b> — Analyze texts for drug promotion and religious extremism\n"
            " 🛡 <b>Group Mode</b> — Protect group members from cyberbullying and harassment 24/7\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📂 <i>Use the menu below to explore system commands and additional info:</i> 👇"
        ),
        "reg_required": (
            "🛡 <b>SafeGuard — Premium Cyber-Security System</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Hello, <b>{name}</b>!\n\n"
            "To fully use our security system and verify your profile, you are required to register.\n\n"
            "📱 <b>To register:</b>\n"
            "Our cyber-system verifies your profile via phone number. This is necessary to secure your profile and groups.\n\n"
            "🇺🇿 <b>Attention:</b> An <b>Uzbekistan phone number (+998)</b> is required.\n"
            "Registration with foreign numbers is not allowed.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <i>To continue, press the <b>«📱 Share contact»</b> button below:</i>"
        ),
        "phone_not_uz": (
            "🇺🇿 <b>Only Uzbekistan phone numbers are accepted!</b>\n\n"
            "Your Telegram phone number <b>{phone}</b> is not from Uzbekistan.\n\n"
            "❗ An Uzbek number starting with <b>+998</b> is required to register.\n\n"
            "If you have an Uzbekistan number, please update your Telegram profile and try again."
        ),
        "group_added": (
            "🛡 <b>SafeGuard — Intellectual Group Protection Activated!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Hello, group members!\n\n"
            "Group security is now under the professional monitoring of <b>SafeGuard Bot</b>. The system runs in automatic mode:\n\n"
            " 🚫 <b>Phishing & Spam</b> — Malicious files and links are deleted instantly\n"
            " 📷 <b>QR-code Protection</b> — Dangerous QR codes on images are scanned and blocked\n"
            " ⚖️ <b>Warnings & Bans</b> — Users receiving 3 warnings (warns) will be banned from the group\n"
            " 🟢 <b>Quiet Mode</b> — The system does not interfere with safe conversations\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>Admin commands for group control:</b>\n"
            " ▫️ /enable — Activate the protection system\n"
            " ▫️ /disable — Temporarily pause protection\n"
            " ▫️ /status — Check current protection status\n"
            " ▫️ /warn — Give a warning to a violator (reply)\n"
            " ▫️ /warns — View warnings count (reply)\n"
            " ▫️ /unwarn — Remove user warnings (reply)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 <i>The system operates based on SafeGuard analysis and protection modules.</i>"
        ),
        "admin_only": "⛔ This command is only for the bot owner!",
        "admin_only_alert": "⛔ Admins only!",
        "group_admin_only": "⛔ This command is only for group administrators!",
        "register_first": (
            "⚠️ Register first!\n\nClick /start."
        ),
        "channel_subscribe_required": (
            "📢 <b>Subscribe to the official SafeGuard channel!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 Dear <b>{name}</b>, to fully use the bot,\n"
            "you must subscribe to our official channel.\n\n"
            "📌 What is on the channel?\n"
            " 🔐 Cybersecurity news\n"
            " ⚠️ Alerts about new threats\n"
            " 💡 Useful tips and guides\n"
            " 🛡 Bot updates and new features\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <b>Go to the channel using the button below, subscribe, and click «✅ Verify»:</b>"
        ),
        "channel_subscribe_success": (
            "✅ <b>Thank you! Subscription confirmed.</b>\n\n"
            "Now you can fully use the bot 🛡"
        ),
        "channel_subscribe_fail": (
            "❌ <b>You haven't subscribed to the channel yet!</b>\n\n"
            "Please subscribe to {channel} channel first,\n"
            "then click the <b>«✅ Verify»</b> button."
        ),
        "channel_subscribe_fail_alert": (
            "❌ You haven't subscribed to the channel yet!\n\n"
            "Please subscribe to {channel} channel first,\n"
            "then click the «✅ Verify» button."
        ),
        "group_no_invite_link": (
            "🚫 <b>SafeGuard Bot could not join the group!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ The <b>«Invite via link»</b> feature is <b>DISABLED</b> in the group settings.\n\n"
            "Without this feature, SafeGuard Bot cannot configure settings and activate protection.\n\n"
            "Therefore, the bot has <b>automatically left the group</b>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>To fix this:</b>\n\n"
            " 1️⃣ Open group settings\n"
            " 2️⃣ Go to <b>Group Type</b>\n"
            " 3️⃣ Enable <b>«Invite via link»</b> ✅\n"
            " 4️⃣ Add the bot back and grant <b>Admin permissions</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <i>SafeGuard only works in correctly configured groups!</i>"
        )
    }
}


def get_text(key: str, lang: str = "uz") -> str:
    """Helper to fetch localized templates. Defaults to Uzbek Latin."""
    lang_dict = LOCALIZED_TEXTS.get(lang, LOCALIZED_TEXTS["uz"])
    return lang_dict.get(key, LOCALIZED_TEXTS["uz"].get(key, ""))


# Legacy constants for module compatibility
ADMIN_ONLY = "👑 Ushbu buyruq faqat bot adminlari uchun!"
ADMIN_ONLY_ALERT = "👑 Faqat bot adminlari uchun!"
REGISTER_FIRST = "📱 Botdan foydalanish uchun ro'yxatdan o'tishingiz lozim!"
