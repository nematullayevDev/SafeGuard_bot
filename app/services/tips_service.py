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
    # 16
    (
        "🔌 <b>Jamoat joylaridagi USB zaryadlovchilar xavfi (Juice Jacking)!</b>\n\n"
        "Aeroport, vokzal yoki kafelardagi bepul USB zaryadlash portlari orqali viruslar yuqishi mumkin.\n\n"
        "❌ <b>Xavf nimada:</b>\n"
        "  • USB kabel ham tok, ham ma'lumot uzatish xususiyatiga ega\n"
        "  • Soxta zaryadlovchi portlar telefoningizdagi parollarni o'g'irlashi mumkin\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Har doim o'zingizning shaxsiy adapteringizdan (rozetkadan) foydalaning\n"
        "  • Maxsus «USB blocker» (faqat tok o'tkazuvchi adapter) ishlating\n"
        "  • Powerbank olib yuring\n\n"
        "🛡️ <i>Telefoningizni begona USB portlarga ulamang!</i>"
    ),
    # 17
    (
        "📶 <b>Uy routeri (Wi-Fi) xavfsizligini ta'minlang!</b>\n\n"
        "Routerning standart paroli o'zgartirilmasa, xakerlar uyingizdagi barcha qurilmalarni nazorat qilishi mumkin.\n\n"
        "✅ <b>Muhim qadamlar:</b>\n"
        "  • Router admin panelining standart paroloni murakkab parolga almashtiring\n"
        "  • Wi-Fi tarmog'iga WPA3 yoki WPA2-AES shifrlash standartini o'rnating\n"
        "  • Routerning dasturiy ta'minotini (firmware) muntazam yangilab turing\n"
        "  • Mehmonlar uchun alohida «Mehmon tarmog'i» (Guest Network) oching\n\n"
        "💡 <i>Wi-Fi parolini har 6 oyda o'zgartirib turish tavsiya etiladi!</i>"
    ),
    # 18
    (
        "🧩 <b>Brauzer kengaytmalari (Extensions) xavfi!</b>\n\n"
        "Chrome yoki Firefox-ga o'rnatilgan ba'zi kengaytmalar siz kiritgan parollar va karta raqamlarini kuzatishi mumkin.\n\n"
        "❌ <b>Ehtiyot bo'ling:</b>\n"
        "  • Noma'lum ishlab chiquvchilarning kengaytmalarini o'rnatmang\n"
        "  • Juda ko'p ruxsat talab qiluvchi («Barcha saytlardagi ma'lumotlarni o'qish») plaginlardan saqlaning\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Faqat eng zarur kengaytmalarni qoldiring, qolganini o'chiring\n"
        "  • Rasmiy Web Store-dan yuklang va foydalanuvchilar sharhlarini o'qing\n\n"
        "🛡️ <i>Keraksiz brauzer kengaytmalari — ma'lumotlar sizib chiqishining asosiy sababidir!</i>"
    ),
    # 19
    (
        "💾 <b>Ma'lumotlarni zaxiralash (Backup) qoidasi!</b>\n\n"
        "Ransomware (tovlamachi virus) telefon yoki kompyuteringizni bloklab qo'ysa, zaxira nusxasi sizni qutqaradi.\n\n"
        "✅ <b>3-2-1 Zaxiralash qoidasi:</b>\n"
        "  • <b>3 ta</b> nusxa yarating (1 ta original + 2 ta zaxira)\n"
        "  • <b>2 xil</b> qurilmada saqlang (masalan, fleshka va kompyuter)\n"
        "  • <b>1 ta</b> nusxani uydan tashqarida saqlang (masalan, bulutli xotirada: Google Drive, iCloud)\n\n"
        "💡 <i>Muhim hujjatlar va oilaviy rasmlarni muntazam ravishda zaxiralab boring!</i>"
    ),
    # 20
    (
        "📧 <b>Fishing elektron xatlaridan saqlaning!</b>\n\n"
        "Email orqali keladigan ko'plab xatlar sizni soxta bank yoki ijtimoiy tarmoq sahifasiga yo'naltiradi.\n\n"
        "🔍 <b>Fishing xatni qanday aniqlash mumkin:</b>\n"
        "  • Jo'natuvchining elektron manzili shubhali bo'ladi (masalan: <code>support@telegram-security-update.com</code>)\n"
        "  • Xatda shoshilinchlik hissi bo'ladi: «Hisobingiz 24 soatda bloklanadi!»\n"
        "  • Havolalar ustiga bosmasdan, kursorni olib borib haqiqiy URL-ni tekshiring\n\n"
        "🛡️ <i>Hech qachon email orqali kelgan havolaga parolingizni kiritmang!</i>"
    ),
    # 21
    (
        "🔒 <b>Ekran qulfini kuchaytiring!</b>\n\n"
        "Qurilmangiz jismonan yo'qolganda yoki o'g'irlanganda, ekran qulfi birinchi himoya hisoblanadi.\n\n"
        "❌ <b>Bunday qulflar zaif:</b>\n"
        "  • Oddiy grafik kalitlar (L, Z, C shakllari oson taxmin qilinadi)\n"
        "  • Oddiy PIN-kodlar: 1111, 1234, tug'ilgan yil\n\n"
        "✅ <b>Tavsiya etiladi:</b>\n"
        "  • Kamida 6 xonali PIN-kod ishlating\n"
        "  • Barmoq izi (Biometrika) va yuzni aniqlash (Face ID) tizimini yoqing\n"
        "  • Ekran o'chgandan keyin avtomatik qulflanish vaqtini 30 sekund qilib sozlang\n\n"
        "📱 <i>Ekran qulfi — shaxsiy hayotingiz kalitidir!</i>"
    ),
    # 22
    (
        "🏠 <b>Aqlli qurilmalar (IoT) xavfsizligi!</b>\n\n"
        "Aqlli kameralar, muzlatgichlar va robot-changyutgichlar xakerlar uyingizga kirishi uchun eshik bo'lishi mumkin.\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Har bir aqlli qurilmaning zavod parolini murakkab parolga almashtiring\n"
        "  • Ularni boshqaradigan mobil ilovalarni muntazam yangilang\n"
        "  • Kameraga ega aqlli qurilmalarni yotoqxona kabi shaxsiy hududlarga o'rnatishdan saqlaning\n\n"
        "💡 <i>IoT qurilmalarini uy Wi-Fi tarmog'idan alohida tarmoqqa ulash xavfsizroqdir!</i>"
    ),
    # 23
    (
        "🔵 <b>Bluetooth tarmog'ini doim yoqiq qoldirmang!</b>\n\n"
        "Bluetooth orqali xakerlar yaqin atrofdagi qurilmalarga ulanishi va ma'lumotlarni o'g'irlashi mumkin.\n\n"
        "❌ <b>Xavflar:</b>\n"
        "  • Begona qurilmalar sizga virusli fayllar yuborishi mumkin\n"
        "  • Qurilmangiz joylashuvini Bluetooth signallari orqali kuzatish oson\n\n"
        "✅ <b>Tavsiya:</b>\n"
        "  • Bluetooth-ni faqat foydalanayotgan vaqtingizda yoqing, qolgan vaqtda o'chirib qo'ying\n"
        "  • Noma'lum ulanish so'rovlarini rad eting (Decline)\n\n"
        "🛡️ <i>Xavfsizligingiz uchun Bluetooth nomini shaxsiy ismingiz bilan atamang!</i>"
    ),
    # 24
    (
        "💳 <b>SIM-kartangizni himoyalang (SIM PIN)!</b>\n\n"
        "SIM-kartangiz o'g'irlansa, firibgarlar uni boshqa telefonga solib, barcha bank va Telegram kodlaringizni olishi mumkin.\n\n"
        "✅ <b>Nima qilish kerak:</b>\n"
        "  • SIM-karta uchun maxsus PIN-kod o'rnating\n"
        "  • Sozlamalar → Xavfsizlik → SIM-kartani qulflash (SIM PIN)\n"
        "  • Bu kodni SIM-karta plastik g'ilofidagi PIN1 kodidan bilib olishingiz mumkin\n\n"
        "💡 <i>SIM PIN yoqilganda, telefon o'chib yonganda SIM-karta kod so'raydi va uni o'g'irlab ishlatib bo'lmaydi!</i>"
    ),
    # 25
    (
        "📸 <b>Rasmlardagi yashirin ma'lumotlar (Metadata/EXIF)!</b>\n\n"
        "Siz internetga yuklagan rasmlar ichida siz yashaydigan joyning aniq geografik koordinatalari bo'lishi mumkin.\n\n"
        "❌ <b>Xavf nimada:</b>\n"
        "  • EXIF metadatalari rasm qaysi telefonda, qachon va aniq qayerda olinganini saqlaydi\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Telefon kamerasida «Geotagging» (joylashuvni saqlash) funksiyasini o'chirib qo'ying\n"
        "  • Telegram orqali rasm yuborganda uni «Fayl» sifatida emas, balki oxirgi rasm sifatida yuboring (Telegram rasmlarni siqqanda metadatalarni o'chiradi)\n\n"
        "🛡️ <i>Shaxsiy xavfsizligingiz uchun uyingiz rasmini joylashuv ma'lumotlari bilan ulashmang!</i>"
    ),
    # 26
    (
        "🛡️ <b>Ilovalarga berilgan ruxsatlarni (Permissions) tekshiring!</b>\n\n"
        "Oddiy kalkulyator yoki o'yin ilovasi telefoningizdagi kontaktlar, kamera va mikrofonni so'rasa — bu shubhali!\n\n"
        "✅ <b>Nima qilish kerak:</b>\n"
        "  • Telefon sozlamalaridan «Ilovalar ruxsati» (App Permissions) bo'limini oching\n"
        "  • Har bir ilova faqat o'ziga tegishli ruxsatlarga ega ekanligini tekshiring\n"
        "  • Ishlatmaydigan ilovalarga kamera va mikrofondan foydalanishni taqiqlang\n\n"
        "💡 <i>Kamroq ruxsat berish — ma'lumotlar xavfsizligining oltin qoidasidir!</i>"
    ),
    # 27
    (
        "🔒 <b>HTTPS va HTTP farqi — xavfsiz ulanish!</b>\n\n"
        "Saytlarga kirganda manzil satridagi qulflash (lock) belgisiga e'tibor bering.\n\n"
        "❌ <b>HTTP saytlar xavfli:</b>\n"
        "  • Bu saytlar ma'lumotlarni shifrlamasdan uzatadi. Jamoat Wi-Fi tarmog'ida parollaringizni osongina o'g'irlash mumkin.\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Faqat <b>HTTPS://</b> bilan boshlanadigan xavfsiz saytlardan foydalaning\n"
        "  • Saytda qulf belgisi qizil yoki ustiga chizilgan bo'lsa, u yerga shaxsiy ma'lumotlar kiritmang\n\n"
        "🛡️ <i>SafeGuard bot barcha taqdim etilgan havolalarning xavfsizligini tekshiradi!</i>"
    ),
    # 28
    (
        "📞 <b>Vishing — Telefon orqali fishingdan ogoh bo'ling!</b>\n\n"
        "O'zini bank xodimi yoki xavfsizlik xizmati deb tanishtirib, qo'ng'iroq qiluvchilar — firibgarlar!\n\n"
        "❌ <b>Ularning bahonalari:</b>\n"
        "  • «Sizning kartangizdan pul yechib olinmoqda, tezda kodni ayting»\n"
        "  • «Hisobingizni blokdan chiqarish uchun SMS kodni aytishingiz kerak»\n\n"
        "✅ <b>Nima qilish kerak:</b>\n"
        "  • Suhbatni darhol to'xtating\n"
        "  • Bankning rasmiy raqamiga (karta orqasidagi raqam) o'zingiz qayta qo'ng'iroq qiling\n\n"
        "🛡️ <i>Hech qaysi bank xodimi sizdan telefonda SMS kodni so'rashga haqli emas!</i>"
    ),
    # 29
    (
        "📥 <b>Faqat rasmiy manbalardan yuklang!</b>\n\n"
        "Telegram guruhlarida tarqalgan soxta dasturlar yoki bepul premium o'yinlar ichida viruslar yashirin bo'ladi.\n\n"
        "🚫 <b>Yuklamang:</b>\n"
        "  • «Bepul Telegram Premium», «Karta balansini ko'paytirish» kabi soxta modlar\n"
        "  • Noma'lum forum va saytlardan o'yin kraklarini (.exe, .dmg)\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Dasturlarni faqat rasmiy saytlar yoki Play Store / App Store-dan yuklang\n"
        "  • Har qanday APK-faylni ochishdan avval SafeGuard-ga yuboring\n\n"
        "🛡️ <i>1 ta xavfli fayl butun qurilmangizni boshqarish imkonini xakerlarga berishi mumkin!</i>"
    ),
    # 30
    (
        "🧠 <b>Sun'iy intellekt firibgarligi (Deepfakes & Voice Clones)!</b>\n\n"
        "Firibgarlar yaqinlaringizning ovozi yoki yuzini taqlid qilib, sizdan pul so'rashi mumkin.\n\n"
        "❌ <b>Qanday amalga oshiriladi:</b>\n"
        "  • Telegramda do'stingizning profili buziladi va sizga uning ovozli xabari keladi (AI yordamida soxtalashtirilgan ovoz)\n\n"
        "✅ <b>Qoidalar:</b>\n"
        "  • Shubhali pul so'rash holatlarida do'stingizga boshqa kanal orqali (masalan, telefon qilib) bog'laning\n"
        "  • Oila a'zolaringiz bilan faqat o'zingiz biladigan maxfiy «kod so'z» kelishib qo'ying\n\n"
        "🛡️ <i>Kiber-tahdidlar rivojlanmoqda, ziyrak va shubhalanuvchan bo'ling!</i>"
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
