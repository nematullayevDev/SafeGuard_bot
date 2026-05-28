"""Service providing daily cybersecurity tips in Uzbek."""
import random

TIPS = [
    # 1
    (
        "🔗 <b>Begona havolalarni ochmang!</b>\n\n"
        "Telegram, WhatsApp yoki SMS orqali kelgan noma'lum havolalar "
        "sizning shaxsiy ma'lumotlaringizni o'g'irlashi mumkin.\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Havolani ochishdan avval SafeGuard botga yuboring\n"
        "  • URL manzilida imlо xatolari bo'lsa — fishing!\n"
        "  • «Bepul», «Yutdingiz», «Tezda bosing» — 100% firibgarlik\n\n"
        "🛡️ <i>Shubhali havolani SafeGuard botga yuboring — 70+ antivirus bilan tekshiriladi!</i>"
    ),
    # 2
    (
        "🔒 <b>Kuchli parol — asosiy himoya!</b>\n\n"
        "Zaif parollar kiber-jinoyatchilarning eng yaxshi do'sti.\n\n"
        "❌ <b>Bunday parollar xavfli:</b>\n"
        "  • 123456 • password • ism+tug'ilgan yil\n\n"
        "✅ <b>Kuchli parol shunday bo'ladi:</b>\n"
        "  • Kamida 12 ta belgi\n"
        "  • Katta va kichik harflar: Aa\n"
        "  • Raqamlar va belgilar: 7 @#$\n"
        "  • Misol: <code>SafeG@rd#2026!</code>\n\n"
        "💡 <i>Har bir sayt uchun alohida parol ishlating!</i>"
    ),
    # 3
    (
        "📱 <b>Ikki bosqichli himoya (2FA) yoqing!</b>\n\n"
        "Parolingiz o'g'irlansa ham 2FA himoyangizni buzib bo'lmaydi.\n\n"
        "✅ <b>Qayerda yoqish kerak:</b>\n"
        "  • Telegram: Sozlamalar → Maxfiylik → Ikki bosqichli\n"
        "  • Google: myaccount.google.com → Xavfsizlik\n"
        "  • Instagram: Sozlamalar → Xavfsizlik → 2FA\n"
        "  • Bank ilovasi: Sozlamalar → Xavfsizlik\n\n"
        "🛡️ <i>2FA yoqilgan hisob 99% xavfsizroq bo'ladi!</i>"
    ),
    # 4
    (
        "📦 <b>Noma'lum fayllarni yuklamang!</b>\n\n"
        "Virusli fayllar ko'pincha zararsiz ko'rinib keladi.\n\n"
        "🚫 <b>Ehtiyot bo'ling:</b>\n"
        "  • .apk — noma'lum manba Android dasturlari\n"
        "  • .exe — Windows dasturlari\n"
        "  • .pdf, .docx — makros virus bo'lishi mumkin\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Ilovalarni faqat Play Store / App Store dan yuklab oling\n"
        "  • Faylni SafeGuard botga yuboring — antivirus tekshiradi\n\n"
        "🛡️ <i>1 ta virusli APK butun telefoningizni nazorat olishi mumkin!</i>"
    ),
    # 5
    (
        "📷 <b>QR-kodlardan ehtiyot bo'ling!</b>\n\n"
        "Firibgarlar QR-kod ichiga xavfli havolalar yashiradi.\n\n"
        "❌ <b>Xavfli QR-kodlar qayerda bo'ladi:</b>\n"
        "  • Begona rasmlar va posterlarda\n"
        "  • Telegram va WhatsApp xabarlarida\n"
        "  • Ko'chada yopishtirilgan soxta QR-kodlarda\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • QR-kodni ochishdan avval SafeGuard botga yuboring\n"
        "  • Bank QR-kodlari rasmiy ilova orqali skanerlang\n\n"
        "🛡️ <i>SafeGuard guruhga yuborilgan barcha QR-kodlarni avtomatik tekshiradi!</i>"
    ),
    # 6
    (
        "💳 <b>Bank ma'lumotlaringizni himoyalang!</b>\n\n"
        "Hech qachon telefon yoki Telegram orqali bank ma'lumotlarini bermang.\n\n"
        "🚫 <b>Hech kimga bermang:</b>\n"
        "  • Karta raqami (16 xona)\n"
        "  • CVV/CVC kod (orqa tarafdagi 3 xona)\n"
        "  • SMS tasdiqlash kodi (OTP)\n"
        "  • Internet banking paroli\n\n"
        "⚠️ <i>Bank hech qachon SMS yoki Telegram orqali bu ma'lumotlarni so'ramaydi!</i>"
    ),
    # 7
    (
        "📶 <b>Jamoat Wi-Fi xavfli bo'lishi mumkin!</b>\n\n"
        "Kafe, metro yoki markazlardagi bepul Wi-Fi orqali xakerlar "
        "ma'lumotlaringizni ushlab olishi mumkin.\n\n"
        "🚫 <b>Ochiq Wi-Fi da qilmang:</b>\n"
        "  • Bank ilovasiga kirmang\n"
        "  • Parol kiritmang\n"
        "  • Muhim hujjatlar yuklash/yuborishdan saqlaning\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • VPN ishlating\n"
        "  • Faqat https:// saytlarga kiring\n\n"
        "🛡️ <i>Mobil internet — jamoat Wi-Fi dan xavfsizroq!</i>"
    ),
    # 8
    (
        "🤖 <b>Fishing SMS va qo'ng'iroqlardan saqlaning!</b>\n\n"
        "«Sizning kartangiz bloklandi», «Yutdingiz» kabi xabarlar — firibgarlik!\n\n"
        "❌ <b>Soxta xabarlar namunasi:</b>\n"
        "  • «Click.uz dan 500,000 so'm yutdingiz! Havola: ...»\n"
        "  • «Payme kartangiz bloklandi, tasdiqlang: ...»\n"
        "  • «Soliq xizmati: jarima to'lang: ...»\n\n"
        "✅ <b>Nima qilish kerak:</b>\n"
        "  • Havolani ochmang\n"
        "  • Raqamni bloklang\n"
        "  • Yaqinlaringizga ogohlantiring\n\n"
        "🛡️ <i>Shubhali havolani SafeGuard botga yuboring!</i>"
    ),
    # 9
    (
        "🔄 <b>Tizimlarni yangilab turing!</b>\n\n"
        "Eskirgan dasturlar xakerlar uchun ochiq eshik.\n\n"
        "✅ <b>Muntazam yanglang:</b>\n"
        "  • Telefon operatsion tizimi (Android/iOS)\n"
        "  • Telegram, bank ilovalari\n"
        "  • Antivirus dasturlari\n"
        "  • Kompyuter Windows/macOS\n\n"
        "💡 <b>Avtomatik yangilanishni yoqing:</b>\n"
        "  • Android: Play Store → Sozlamalar → Avtomatik yangilash\n"
        "  • iOS: Sozlamalar → App Store → Avtomatik yangilanishlar\n\n"
        "🛡️ <i>Ko'pchilik xurujlar yangilanmagan tizimlar orqali amalga oshiriladi!</i>"
    ),
    # 10
    (
        "👁️ <b>Ijtimoiy muhandislikdan saqlaning!</b>\n\n"
        "Xakerlar texnik usullar o'rniga sizni aldash orqali ma'lumot oladi.\n\n"
        "❌ <b>Klassik aldov usullari:</b>\n"
        "  • «Men bank xodimiman, kartangizni tasdiqlang»\n"
        "  • «Siz tanlangiz, sovg'a olish uchun kod yuboring»\n"
        "  • «Do'stingiz xavfda, pul o'tkazing»\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Shoshilib qaror qabul qilmang\n"
        "  • Do'stingizni to'g'ridan-to'g'ri qo'ng'iring, tekshiring\n"
        "  • Hech qachon SMS kodni hech kimga bermang\n\n"
        "🛡️ <i>Eng kuchli «antivirus» — sizning ziyrakligingiz!</i>"
    ),
    # 11
    (
        "🌐 <b>Ijtimoiy tarmoqlarda ehtiyot bo'ling!</b>\n\n"
        "Instagram, Telegram, Facebook profilingizdagi ma'lumotlar "
        "firibgarlar uchun qurol bo'lishi mumkin.\n\n"
        "🚫 <b>Ochiq profilga qo'ymang:</b>\n"
        "  • To'liq uy manzilingiz\n"
        "  • Tug'ilgan sanangiz (parol taxmini uchun ishlatiladi)\n"
        "  • Telefon raqamingiz\n"
        "  • Sayohat va ta'til rejalari (uy bo'sh qolishini bildiradi)\n\n"
        "✅ <i>Profilingizni «Shaxsiy» (Private) rejimga o'tkazing!</i>"
    ),
    # 12
    (
        "🕵️ <b>Kiberbulling — jinoyat!</b>\n\n"
        "Internet orqali tahdid, haqorat yoki sharmandali kontent tarqatish "
        "O'zbekiston qonunchiligida jinoiy javobgarlikka tortiladi.\n\n"
        "⚖️ <b>Huquqiy asoslar:</b>\n"
        "  • O'zR JK 140-modda — Haqorat (jarima yoki qamoq)\n"
        "  • O'zR JK 139-modda — Tuhmat\n"
        "  • O'zR JK 141-modda — Shaxsiy hayotga tajovuz\n\n"
        "✅ <b>Nima qilish kerak:</b>\n"
        "  • Skrinshot oling — dalil saqlab qoling\n"
        "  • Bloklang\n"
        "  • Kiberjinoyatlar bo'limiga murojaat qiling: <b>1102</b>\n\n"
        "🛡️ <i>SafeGuard guruhingizni kiberbullingdan 24/7 himoya qiladi!</i>"
    ),
    # 13
    (
        "🔐 <b>Parol menejeri ishlating!</b>\n\n"
        "Har bir sayt uchun alohida kuchli parol eslab qolish qiyin. "
        "Parol menejeri buni avtomatik bajaradi.\n\n"
        "✅ <b>Tavsiya etilgan bepul menejerlar:</b>\n"
        "  • <b>Bitwarden</b> — ochiq manba, bepul\n"
        "  • <b>KeePass</b> — oflayn, bepul\n"
        "  • <b>Google Password Manager</b> — Chrome bilan integratsiya\n\n"
        "🚫 <b>Qilmang:</b>\n"
        "  • Parolni daftarga yozmang\n"
        "  • Telegramda o'zingizga yuborish — xavfli!\n\n"
        "🛡️ <i>1 ta kuchli master parol = barcha parollaringiz xavfsiz!</i>"
    ),
    # 14
    (
        "📵 <b>Telefon yo'qolsa nima qilish kerak?</b>\n\n"
        "Telefoningiz yo'qolsa yoki o'g'irlansa — darhol quyidagilarni bajaring:\n\n"
        "⚡ <b>Darhol bajaring:</b>\n"
        "  1. SIM kartani bloklang (operator qo'ng'irig'i)\n"
        "  2. Telegramni boshqa qurilmadan chiqaring\n"
        "       Telegram → Sozlamalar → Qurilmalar → Chiqish\n"
        "  3. Google/Apple hisobingizni bloklang\n"
        "  4. Bank ilovalaringizni bloklang\n\n"
        "💡 <i>Oldindan: Find My Device / Find My iPhone yoqib qo'ying!</i>"
    ),
    # 15
    (
        "🧠 <b>Kiberxavfsizlik — hammaning vazifasi!</b>\n\n"
        "O'zingiz xavfsiz bo'lishingiz yetarli emas — "
        "yaqinlaringizni ham himoya qiling.\n\n"
        "💛 <b>Bugun qiling:</b>\n"
        "  • Ota-onangizga fishing haqida tushuntiring\n"
        "  • Farzandingizning telefonida parental control yoqing\n"
        "  • Do'stingizga 2FA haqida o'rgating\n"
        "  • Guruhingizga SafeGuard botni qo'shing\n\n"
        "🌍 <i>Xavfsiz raqamli O'zbekiston — birgalikda quramiz!</i>\n\n"
        "🛡️ <b>SafeGuard Bot</b> — guruhingizni 24/7 himoya qiladi!"
    ),
]


class TipsService:
    _last_index: int = -1

    def get_daily_tip(self) -> str:
        """Har kuni navbatdagi maslahatni qaytaradi (takrorlanmaydi)."""
        self._last_index = (self._last_index + 1) % len(TIPS)
        tip = TIPS[self._last_index]
        return (
            "💡 <b>KUNLIK KIBERXAVFSIZLIK MASLAHATI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{tip}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ <i>SafeGuard Bot — O'zingiz va guruhingizni himoya qiling!</i>"
        )

    def get_random_tip(self) -> str:
        """Tasodifiy maslahat."""
        tip = random.choice(TIPS)
        return (
            "💡 <b>KUNLIK KIBERXAVFSIZLIK MASLAHATI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{tip}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ <i>SafeGuard Bot — O'zingiz va guruhingizni himoya qiling!</i>"
        )
