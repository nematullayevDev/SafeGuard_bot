"""Initial banned_sites seed data."""
from datetime import datetime

TELEGRAM_ITEMS = [
    "A'ashiqul jannah", "Abdulloh Buxoriy darslari 01", "Abdulloh zufar tavhid",
    "ABDULLOH ZUFAR", "Abdulloh Zufar", "HIJOBIM", "Abduvali Qori Rohimahulloh",
    "Abu Abdulloh Faqih (arabcha)", "Abu Saloh", "Al Shahid", "Alfatx",
    "ALI ANSORIY", "Alloh yo'lida", "Allohning ism va sifatlari",
    "Allohu Akbar", "almuqit_", "An'om surasi tafsir", "An'om surasi tafsiri",
    "ANSOORIY", "DARSLARDAN FOYDALAR", "Darslardan qisqa lavhalar", "DARSLIKLAR",
    "Davatchilar", "Dawatu ar Rasul", "Ahliddin_navqotiy tavhid va jihod",
    "Eslating", "Eslatma", "Islom Nuri", "EX-Muslims I Uzbekistan", "FAKIHUN",
    "Duo qilishdagi odoblar/arab yozuvida", "HALIGACHA PARHEZDAMIZ",
    "HAQ NURI TAVHID", "Hidoya_Sharhi_777", "Hidoyat Darsliklari", "HIDOYAT TV",
    "Hijobiga sodiqlar", "Himmat Darsligi", "Hizb sadoqat uz", "Holis Islom",
    "Ilm bu Nur", "Мухожир Полвон", "Нажот Najot", "Нажот", "Полвон Ака",
    "Полвон Новқатлик", "Роя", "Мухожир Абдуллоҳ", "Muhajir UZ",
    "Muhammad Ismoil", "Аскарали Усмонов", "Usmon Abu Layno", "Yusuf Buxoriy",
    "Musab Tursimamatov", "Абу Ҳамза", "Ислом Баҳори", "Фузайл Ибн Абу Ҳафс",
    "Asadulloh Termiziy", "Суфий Дарвеш", "Jundulloh aka", "Жасур Расулов",
    "Mustafa Alimov", "Yusuf Ofcc", "Умар Али", "Muhammad Usmon",
    "Abdulloh Ibn Abdulloh", "AL Anfal Mediaa", "Ism Shartmas", "Rahmatjon Avazov",
    "Тавҳид Ва Жиҳод", "Туркистон", "Умар Ҳаттоб",
    "Халид Арабий", "Ҳасан Қодиров", "Хурриат инфо", "Хўжа Бува",
    "Банда Ожиз", "Jeck Vorobey", "Sakina Karvanji", "Ehson ilm",
    "Mo'tasim Billah", "AL Ahirat Medya", "Mansur Amin", "UzTurkiston Uz",
    "Haq va Batil", "Nurmuhammad Aka", "Абу Умар Толибон",
    "Абу Юсуф Парпиев", "Nodirbek Umarov", "Абдуллоҳ Муслим", "Абу Абдулҳамид",
    "Asadulloh Turkiy", "Abu Dardo", "Abu Jihad", "Muhammad AbuAhmad",
    "Ал-Вақия TV", "Муҳаммад Тоҳир", "Юсуф Зайд", "Тавҳид Аллоҳни Танитиш",
    "Фаррухбек Абдуллаев", "Фарук Шами (Фарук Шами)", "Райёна Муҳаммеджановна",
    "Чындык Ақыйқат", "Abdujalil Qodirov", "Murat Turk Abdullah",
    "Abu Muso", "Ахмад Одил (Odiljon Jalilov)", "Mahmud Adilov", "Муминжон Абдуллаев",
    "Xolis Nazar", "Muhsiniy Abdulloh", "Mubin Najib", "Ойша Муҳаммад",
    "Abu Turob (Абу Туроб)", "Hijratga Yo'l Olgan Banda", "Sardorbek Nurullayev",
    "Амирхан Ташкентбаев", "Ал Қассам", "Abu Usaymin", "Фатхия Туркистоний",
    "Ahmad Muhammad", "Muoz Andalusiy", "Abu Umar Tolibon", "Муҳаммад Али",
    "Abu Dujana", "Муҳаммад Солиҳ Муҳаммад Яъқуб", "Мусофир Жаҳонгашта",
    "Yusuf Media sahifasi", "Салоҳиддин Айюбий", "СалоҳиддинМуслим (Muslim)",
    "Абдуллоҳ Абдуллоҳ", "Гриша Иванов", "Алихонтўра Шокиржон ўғли",
    "Абдужалил Кодиров (Odiljon jalilov)", "Islom Abu Khalil", "Mehmon Adolad",
    "Ғуроба Медиа", "_taqvodor_yigit_100", "Абдулазиз Ҳошим", "Султон Сайфуллоҳ",
    "Салоҳиддин Муслим (Hidoyat)", "Муҳаммад Туркистоний",
    "Akrom Maxmudov", "Madinauchun Madinauchun", "Abu Valid",
]

YOUTUBE_ITEMS = [
    "Abdulloh Ayyub", "Abdulloh Islamiy", "abror ibn abdulloh", "Foruq Uz",
    "GURABA", "Hidoyat Izlab", "HIDOYAT TV", "Islam Abu Khalil",
    "Islamic talks", "ISLOM TONGI", "ALHAQ_TV", "Alijon Aliev", "AL-IXLOS",
    "ANTI. KAZZOB", "Aqiyda darslari", "Aqiydatul vositiya", "Asl haq",
    "Ayollar darslari silsilasi", "BAYYINA TV", "Da'vat Media",
    "DA'VAT UZ", "Darslardan qisqa lavhalar", "Darsliklar", "Davat Uz",
    "DIN FAXRI", "Ehson tv", "Fiqh ahkomlari", "Foida Mp3", "AHLI ZIKR",
    "Ahli-sunna Tv", "Al Buhoriy Tv", "IXLOC TV", "JANNATGA YO'L",
    "Jannatga Yo'l", "Mahmud Abdulmomin", "Muhim darslar", "MUHOJIR UZ",
    "Muhsin TV", "MUSLIM TV", "Mustalahul hadis",
    "omar alhamed", "Qalb Nuri", "Saad Muhtor", "Saad Muxtor 2",
    "SAAD MUXTOR", "Risolat Hazinasi", "Savol va javoblar",
    "sheriyat olami", "Yusuf Media", "HIDOYAT YO'LI", "Zaytun TV",
    "ZufarMedia", "Islom Bahori", "Salomat qalb", "Allohu Ahad",
    "Shayx Abduvali Qori", "Al Waqiyah TV-UZ", "AL-ANFAL MEDIA",
    "Siyrat", "solixlargulshani", "Tafsir darslari", "Qiyomatdan avvalgi fitnalar",
    "Shom media", "Silsilaviy darslar va ma'ruzalar",
    "Islom Dinim Media Sahifasi",
    "Islomni buzuvchi amallar darslari",
    "Talabalar uchun darslar", "Talbisu iblis darslari", "TamKin Media",
    "TAQVO MEDIA TV", "Tavhid darsi",
    "Tavhid Maktabi", "The Saroy Mulla!", "Turkiston", "USTOZLAR DAVATLARI",
    "Usulul fiqh", "Uzbek uz", "Uzr Yoq", "Xolis Media", "Alfatx",
    "Foida va qoidalar", "Ечим Исломда",
    "ал-Ваъй", "АЛ-ФАТХ ТВ", "АЛЬ-ФАТҲ ТВ", "АЛЬ ФАТХ ТВ", "sodiqlar uz",
    "TavhidOrg Sahifasi I Rasmiy", "Yaumma", "Iymonli Qalblar",
    "MUSLIM TV Sahifasi", "AL-FATX STUDIO", "UMMAT SHERI", "Taqvo Media",
    "ТАУХИД медиа", "hidoyat islom tarixi", "Nomoz va benomozga taluqli masalalar",
    "СОЛИХА САТТАРОВА", "Куддус хакида тахлил", "Rushda Huda", "Muhojir Podcast",
    "Хизб-ни Аъзоси Ноокатлик Полвон Ака", "Иброҳим Муваҳҳидм",
    "ISLOM ULAMOLARI ИСЛОМ УЛАМОЛАРИ",
    "Ўзбекистонда топмагандим Яҳудийлар кўп жойда топдим",
    "uch_asos_27 номли аудио ва видео шаклда фикр, маъруза ва фатволар",
]

INSTAGRAM_ITEMS = [
    "alloh__yolida__", "abu_ismoil", "mujaheed", "chamanzoriy",
    "abusalohhafizulloh2", "abuxolid_xuroson", "AHLI ZIKR", "Abdulloh Zufar",
    "usoma_navqotiy", "al_ahirat", "davat_tv", "muvahhid", "haq_axli",
    "Haqni Izlab", "gruppa_quron_114", "GURABA. UZ", "halid4647", "Bilol Sohib",
    "shayh_sodiq_samarqandiy", "Tohirjon yuldashev", "Abdulloh Toshkandiy",
    "Bozorov Muhammadjon", "Mister", "shahidlar qoni uchunn",
    "muhammadmirzayevm_", "Muhojir tactical", "MuhsinTV Ma'muriyati",
    "instagram.com/r_muslim1", "instagram.com/tavhid.risolasi",
    "instagram.com/ya_ummati571", "instagram.com/ukkoshaa.77",
    "SHAYX USMON AL-HOMIS FATVO VA DARSLIKLARI",
    "instagram.com/halilulloh.salaf", "instagram.com/islomga_davat_1",
    "instagram.com/abu_.ashraff",
]

FACEBOOK_ITEMS = [
    "facebook.com/ali.abuasiya.5",
    "facebook.com/profile.php?id=100082238465890",
    "facebook.com/algahujum.algahujum.5",
    "Xalifalilik davlati uchun harakat — kufrning barcha xijjalariga rag'batlantiruvchi sahifa",
    "Ҳизб ут-Таҳрир амири улуғ олим Ато ибн Халил Абу Роштанинг Халифалик кулатилганининг аламли юз йиллик хотираси муносабати билан сўзлаган нутқи",
    "Terroristik tashkilotlar sahifalari",
    "Nafrat nutqini tarqatuvchi sahifalar",
    "Zo'ravonlikni qo'llab-quvvatlovchi sahifalar",
]

TWITTER_ITEMS = [
    "Terroristik tashkilotlar akkauntlari",
    "Ekstremistik g'oyalar tarqatuvchi akkauntlar",
    "Nafrat nutqi tarqatuvchi akkauntlar",
    "Dezinformatsiya tarqatuvchi akkauntlar",
    "Noqonuniy kontent havola qiluvchi akkauntlar",
    "Xalifalilik g'oyalarini targ'ib qiluvchi akkauntlar",
]

WHATSAPP_ITEMS = [
    "Terroristik tashkilotlar guruhlari",
    "Narkotik moddalar sotuvchi guruhlar",
    "Noqonuniy qimorbozlik guruhlari",
    "Pornografik kontent guruhlari",
    "Ekstremistik mafkurani tarqatuvchi guruhlar",
    "Firibgarlik va fishing guruhlari",
]

TIKTOK_ITEMS = [
    "18+ yoshga mo'ljallangan kontentlar",
    "Zo'ravonlikni targ'ib qiluvchi videolar",
    "Narkotik moddalarni ko'rsatuvchi videolar",
    "Ekstremistik g'oyalar videolari",
    "Noqonuniy faoliyatni namoyish etuvchi videolar",
    "Bolalarga zarar yetkazuvchi challenge'lar",
    "Terroristik kontent tarqatuvchi akkauntlar",
]

SEED_MAP = {
    "telegram": TELEGRAM_ITEMS,
    "youtube": YOUTUBE_ITEMS,
    "instagram": INSTAGRAM_ITEMS,
    "facebook": FACEBOOK_ITEMS,
    "twitter": TWITTER_ITEMS,
    "whatsapp": WHATSAPP_ITEMS,
    "tiktok": TIKTOK_ITEMS,
}


def seed_banned_sites(cursor) -> None:
    """Idempotently insert default banned-site entries."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    for platform, items in SEED_MAP.items():
        for name in items:
            cursor.execute(
                "INSERT OR IGNORE INTO banned_sites (platform, name, added_at, is_new) "
                "VALUES (?, ?, ?, 0)",
                (platform, name, now),
            )
