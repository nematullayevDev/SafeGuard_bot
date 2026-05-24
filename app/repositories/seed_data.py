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


def seed_forensics(cursor) -> None:
    """Idempotently insert default forensics cases if table is empty."""
    cursor.execute("SELECT COUNT(*) FROM forensics")
    if cursor.fetchone()[0] > 0:
        return

    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # 30 items
    mock_cases = [
        # Extremism
        (-1001234567890, "Toshkent Bozor", 123456701, "Alisher Umarov", "alisher_u", "+998901234561",
         "Bizga demokratiya kerak emas, faqat xalifalik qonunlari ostida yashashimiz kerak!", "extremism",
         "Diniy radikalizm va konstitutsiyaviy tuzumga qarshi da'vat.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456702, "Bobur Alimov", "bobur_a", "+998901234562",
         "Абу Салоҳ маърузаларини тингланг, ҳақиқий жиҳод йўли ҳақида гапирган.", "extremism",
         "Taqiqlangan ekstremistik voiz ma'ruzalari targ'iboti (Cyrillic).", now, None),
        (-1001234567890, "Toshkent Bozor", 123456703, "Diyor Xoliqov", "", "",
         "Taqiqlangan jihodiy nashida yuklayapman, hamma eshitsin.", "extremism",
         "Diniy ekstremistik audio/nashida targ'iboti.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456704, "Eldor Karimov", "eldor_k", "+998935552211",
         "Ҳизб ут-Таҳрир варақаларини тарқатиш вақti келди.", "extremism",
         "Taqiqlangan Hizb ut-Tahrir tashkiloti materiallari targ'iboti.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456705, "Farrux Qodirov", "farrux_q", "",
         "Xalifalikni tiklash yo'lida hammamiz birlashishimiz lozim, boshqa yo'l yo'q.", "extremism",
         "Diniy radikal g'oyalar va konstitutsiyaviy tuzumni ag'darishga da'vat.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456706, "G'ofur Ergashev", "gofur_e", "+998946663322",
         "Суриядаги biродарларимизга ёрдам бериш учун маблағ йиғиляпти, қўшилинг.", "extremism",
         "Taqiqlangan terrorchi guruhlarni moliyalashtirishga da'vat.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456707, "Hasan Usmonov", "hasan_u", "",
         "Tavhid va Jihod guruhining yangi darsligi chiqdi. Link orqali o'ting.", "extremism",
         "Taqiqlangan 'Tavhid va Jihod katibasi' materiallari targ'iboti.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456708, "Ilyos Karimov", "ilyos_k", "+998909998877",
         "Дунё куфр ботқоғига ботди, фақат қуролли жиҳод бизni қутқаради.", "extremism",
         "Diniy jangarilik va qurolli jihodga chaqiriq.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456709, "Jasur Solihov", "jasur_s", "",
         "Biz radikal diniy guruhlarga qo'shilishimiz va tog'ut hukumatga qarshi chiqishimiz kerak.", "extremism",
         "Konstitutsiyaviy tuzumga qarshi radikal chaqiriq.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456710, "Kamola Axmedova", "kamola_a", "+998971112233",
         "Мужоҳидларнинг жасорати ҳақида видеоролик, кўринг ва тарқатинг.", "extremism",
         "Jangarilar faoliyatini ulug'lash va targ'ib qilish.", now, None),
         
        # Drugs
        (-1001234567890, "Toshkent Bozor", 123456711, "Lola Saidova", "lola_s", "",
         "Klad va kuryerlik ishlari bor, oylik 1000$. Hamma ma'lumot lichkada, yozinglar.", "drugs",
         "Giyohvand moddalarni yashirin joylash (klad/kuryer) bo'yicha ish taklifi.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456712, "Murod Ergashev", "murod_e", "+998901234572",
         "Кристалл ва меф сотиiladi. Тошкент бўйича заклад бор, сифати зўр.", "drugs",
         "Metamfetamin (kristall/mef) noqonuniy savdosi targ'iboti.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456713, "Nodir Karimov", "nodir_k", "",
         "Lyrika va tramadol bor, shoshiling. Eng arzon narxlarda.", "drugs",
         "Tarkibida psixotrop moddalar bo'lgan dori-darmonlar noqonuniy aylanmasi.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456714, "Olim Tojiyev", "olim_t", "+998934445566",
         "Бомба сифатли наша келди. Оптом олувчиларга чегирма бор, ёзинг.", "drugs",
         "Marixuana (nasha) sotuvi va ommaviy reklama.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456715, "Po'lat Sabirov", "polat_s", "",
         "Spays sotib olishni xohlovchilar bormi? Toshkent shahrida tayyor joylar bor.", "drugs",
         "Sintetik narkotik (spays) savdosi va yashirin manzillar.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456716, "Qobil Ergashev", "qobil_e", "+998947775533",
         "Экстази таблеткалари бор, оригинал. Клубда дам олиш учун зўр.", "drugs",
         "Psixotrop tabletkalar (ekstazi/MDMA) noqonuniy aylanmasi.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456717, "Rustam Axmedov", "rustam_a", "",
         "Koks sotiladi, toza mahsulot. Yetkazib berish bepul.", "drugs",
         "Kokain (koks) giyohvandlik moddasi savdosi da'vati.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456718, "Sardor Alimov", "sardor_a", "+998902223344",
         "Героин бор, сифати кафолатланган. Қизиққанлар шахсийга ёзсин.", "drugs",
         "Geroin noqonuniy savdosi targ'iboti.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456719, "Temur Qodirov", "temur_q", "",
         "Giyohvandlik moddalari kanali ochildi, kiring va tanlang.", "drugs",
         "Narkotik moddalar sotiladigan noqonuniy kanal reklamasi.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456720, "Umid Ergashev", "umid_e", "+998978889900",
         "Гашиш бор, Тошкент бўйича заклад. Тез ёзинг, сони кам қолди.", "drugs",
         "Gashish giyohvandlik moddasi savdosi.", now, None),
         
        # Bullying
        (-1001234567890, "Toshkent Bozor", 123456721, "Vali Usmonov", "vali_u", "",
         "Sen iflosni sharmanda qilaman, barcha rasmlaringni internetga tarqataman!", "bullying",
         "Kiberbulling, tovlamachilik va shaxsiy ma'lumotlarni tarqatish tahdidi.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456722, "Xurshid Alimov", "xurshid_a", "+998903334455",
         "Агар пул бермасанг, сеni ўлдираман! Соғ қолмайсан, кўчага чиқма.", "bullying",
         "Kiber-tahdid va shaxsiy xavfsizlikka jiddiy tahdid (Cyrillic).", now, None),
        (-1001234567890, "Toshkent Bozor", 123456723, "Yodgor Xoliqov", "", "",
         "Bu guronhdagi hamma seni yomon ko'radi, o'zingni osib qo'ya qol, yashashdan nima foyda?", "bullying",
         "O'zini o'zi o'ldirishga undash va og'ir ruhiy kiberbulling.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456724, "Zokir Karimov", "zokir_k", "+998938887766",
         "Сени кўрганимда сўяман, тирик қолмайсан, мендан қочиб қутулолмайсан.", "bullying",
         "Suiqasd va shaxsiyatga qaratilgan og'ir jismoniy tahdid.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456725, "Anvar Sabirov", "anvar_s", "",
         "Sening oilangni sharmanda qiladigan videolar bor menda. Hammaga tarqatib yuboraman.", "bullying",
         "Shantaj va shaxsiy obro'ga tahdid soluvchi materiallar bilan qo'rqitish.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456726, "Bekzod Tojiyev", "bekzod_t", "+998941113355",
         "Сан ифлосни оилангни ҳам, ўзингни ҳам йўқ қилиб юбораман, кутиб тур.", "bullying",
         "Oila a'zolariga nisbatan kiber-tahdid va zo'ravonlik chaqirig'i.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456727, "Charos Qosimova", "charos_q", "",
         "Ertaga sening barcha sirlaringni ochib guruhga tashlayman, ko'ramiz keyin qanday yashaysan.", "bullying",
         "Shaxsiy sir va ma'lumotlarni ruxsatsiz tarqatish orqali qo'rqitish.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456728, "Davron Ergashev", "davron_e", "+998902224466",
         "Қўрқоқ, сен яшашга нолойиқсан. Бутун шаҳар сени устингдан кулади.", "bullying",
         "Tizimli ruhiy kiberbulling va haqoratlar.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456729, "E'zoza Solihova", "ezoza_s", "",
         "Eriingga hammasini aytib beraman, hayoting barbod bo'ladi. Kutgin.", "bullying",
         "Oilaviy hayotga va shaxsiy munosabatlarga kiber-aralashuv va shantaj.", now, None),
        (-1001234567890, "Toshkent Bozor", 123456730, "Feruz Axmedov", "feruz_a", "+998973336699",
         "Кўчада менга дуч келсанг, жавобини берасан. Соғ кетмайсан.", "bullying",
         "Jismoniy tajovuz qilish haqida jiddiy kiber-tahdid.", now, None)
    ]
    
    cursor.executemany(
        """
        INSERT INTO forensics (
            chat_id, chat_title, user_id, full_name, username, phone,
            message_text, violation_type, reason, detected_at, photo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        mock_cases
    )

