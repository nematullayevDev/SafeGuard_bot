"""Static message templates."""

WELCOME = (
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
)

REG_REQUIRED = (
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
)

PHONE_NOT_UZ = (
    "🇺🇿 <b>Faqat O'zbekiston raqami qabul qilinadi!</b>\n\n"
    "Sizning Telegram raqamingiz <b>{phone}</b> — bu O'zbekiston raqami emas.\n\n"
    "❗ Tizimdan foydalanish uchun <b>+998</b> bilan boshlangan O'zbek raqami talab qilinadi.\n\n"
    "Agar O'zbekiston raqamiga ega bo'lsangiz, Telegram profilingizni shu raqam bilan yangilang va qayta urinib ko'ring."
)

GROUP_ADDED = (
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
)

ADMIN_ONLY = "⛔ Bu buyruq faqat admin uchun!"
ADMIN_ONLY_ALERT = "⛔ Faqat admin!"
GROUP_ADMIN_ONLY = "⛔ Bu buyruq faqat guruh adminlari uchun!"
REGISTER_FIRST = "⚠️ Avval ro'yxatdan o'ting!\n\n/start ni bosing."

CHANNEL_SUBSCRIBE_REQUIRED = (
    "📢 <b>SafeGuard rasmiy kanaliga obuna bo'ling!</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👋 Hurmatli <b>{name}</b>, botdan to'liq foydalanish uchun\n"
    "rasmiy kanalimizga obuna bo'lishingiz shart.\n\n"
    "📌 Kanalda nima bor?\n"
    " 🔐 Kiberxavfsizlik yangiliklari\n"
    " ⚠️ Yangi tahdidlar haqida ogohlantirishlar\n"
    " 💡 Foydali maslahatlar va ko'rsatmalar\n"
    " 🛡 Bot yangiliklari va yangi funksiyalar\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👇 <b>Quyidagi tugmani bosib kanalga o'ting, obuna bo'ling va «✅ Tekshirish» tugmasini bosing:</b>"
)

CHANNEL_SUBSCRIBE_SUCCESS = (
    "✅ <b>Rahmat! Obuna tasdiqlandi.</b>\n\n"
    "Endi botdan to'liq foydalanishingiz mumkin 🛡"
)

CHANNEL_SUBSCRIBE_FAIL = (
    "❌ <b>Siz hali kanalga obuna bo'lmagansiz!</b>\n\n"
    "Iltimos, avval {channel} kanaliga obuna bo'ling,\n"
    "so'ng <b>«✅ Tekshirish»</b> tugmasini bosing."
)

GROUP_NO_INVITE_LINK = (
    "🚫 <b>SafeGuard Bot guruhga qo'shila olmadi!</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "❌ Guruh sozlamalarida <b>«Havola orqali taklif qilish»</b> funksiyasi <b>O'CHIRILGAN</b>.\n\n"
    "Bu funksiya o'chiq bo'lsa, SafeGuard Bot:\n"
    " • Admin panelida guruhni ro'yxatga ola olmaydi\n"
    " • «Bot qaysi guruhlarda» bo'limida ko'rinmaydi\n"
    " • Guruh havolasini saqlayolmaydi\n\n"
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
