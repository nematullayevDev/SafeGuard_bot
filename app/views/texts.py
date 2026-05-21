"""Static message templates."""

WELCOME = (
    "👋 Salom, <b>{name}</b>!\n\n"
    "🛡 Men <b>SafeGuard</b> xavfsizlik botiman.\n\n"
    "Nima qila olaman:\n"
    "🔗 Link yuboring → tekshiraman\n"
    "📦 APK yuboring → tahlil qilaman\n"
    "🚫 Spam xabarlarni aniqlayman\n"
    "👥 Guruhingizni himoya qilaman\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📂 Barcha buyruqlarni ko'rish uchun\n"
    "<b>«Buyruqlar»</b> tugmasini bosing 👇"
)

REG_REQUIRED = (
    "👋 Salom, <b>{name}</b>!\n\n"
    "🛡 Men <b>SafeGuard</b> xavfsizlik botiman.\n\n"
    "📱 Botdan foydalanish uchun avval\n"
    "<b>telefon raqamingiz bilan ro'yxatdan o'ting</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Quyidagi tugmani bosing 👇"
)

GROUP_ADDED = (
    "👋 Salom! Men <b>SafeGuard</b> xavfsizlik botiman.\n\n"
    "✅ Guruh himoyasi <b>AVTOMATIK yoqildi!</b>\n\n"
    "🔴 Xavfli fayl/link → o'chiriladi + ogohlantirish\n"
    "⚠️ 3 ta warn → foydalanuvchi BAN qilinadi\n"
    "✅ Xavfsiz kontent → jim turaman\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "👑 <b>Adminlar uchun buyruqlar:</b>\n\n"
    "▫️ /enable — Himoyani yoqish\n"
    "▫️ /disable — Himoyani o'chirish\n"
    "▫️ /status — Himoya holati\n"
    "▫️ /warn — Foydalanuvchiga ogohlantirish (reply)\n"
    "▫️ /warns — Warn sonini ko'rish (reply)\n"
    "▫️ /unwarn — Warnlarni tozalash (reply)\n"
    "━━━━━━━━━━━━━━━━━━━━"
)

ADMIN_ONLY = "⛔ Bu buyruq faqat admin uchun!"
ADMIN_ONLY_ALERT = "⛔ Faqat admin!"
GROUP_ADMIN_ONLY = "⛔ Bu buyruq faqat guruh adminlari uchun!"
REGISTER_FIRST = "⚠️ Avval ro'yxatdan o'ting!\n\n/start ni bosing."
