"""Service providing daily cybersecurity tips in Uzbek."""
import random

TIPS = [
    "🔒 <b>Murakkab parol ishlating!</b> Hech qachon ism, familiya yoki tug'ilgan yilingizni parol qilmang. Kamida 10-12 belgidan iborat, katta-kichik harflar, raqamlar va maxsus belgilar (#, $, %, @) aralashgan parollar eng xavfsiz hisoblanadi.",
    "🛡️ <b>Ikki bosqichli verifikatsiya (2FA)ni yoqing!</b> Telegram, Google, va ijtimoiy tarmoqlardagi profilingizni himoya qilish uchun faqat SMS/parol bilan cheklanmang, qo'shimcha verifikatsiya parolini (2FA) albatta yoqib qo'ying.",
    "📦 <b>Noma'lum fayllarni yuklamang va ochmang!</b> Ayniqsa, .apk kengaytmali android dasturlar yoki g'alati nomli hujjatlar qurilmangizdagi bank ilovalari va shaxsiy ma'lumotlarni o'g'irlashi (troyanlar) mumkin.",
    "🔗 <b>Fishing havolalardan ehtiyot bo'ling!</b> 'Sizga bepul pul yutug'i beriladi' yoki 'Telegram premium bepul' mazmunidagi soxta saytlar havolasiga kirib, telefon raqamingiz va tasdiqlash kodini aslo kiritmang.",
    "🌐 <b>Ilovalarni faqat rasmiy do'konlardan oling!</b> Google Play yoki App Store rasmiy do'konlaridan tashqari veb-saytlardan yuklangan ilovalar zararli virus va josuslik dasturlarini o'z ichiga olishi mumkin.",
    "📶 <b>Jamoat Wi-Fi tarmoqlaridan ehtiyot bo'ling!</b> Kafe, metro yoki parklardagi ochiq Wi-Fi tarmoqlari orqali muhim shaxsiy profillar yoki bank ilovalariga kirmang, chunki xakerlar tarmoq trafigini kuzatishi mumkin.",
    "🔄 <b>Tizimlarni muntazam yangilab turing!</b> Telefon va kompyuteringiz operatsion tizimi (OS) hamda o'rnatilgan ilovalarni doimiy yangilab turish kiber-jinoyatchilardan himoyalanishning eng oson yo'lidir.",
    "🤖 <b>SafeGuard Botidan foydalaning!</b> Guruhlaringiz xavfsizligini ta'minlash uchun ushbu botni guruhga qo'shib adminlik huquqini bering, bot havolalar va virusli fayllarni 24/7 nazorat qiladi.",
    "🚫 <b>Shubhali xabarlar haqida xabar bering!</b> Agar kimdir sizga reklamalar, noqonuniy materiallar yoki g'alati linklar yuborayotgan bo'lsa, ularga javob bermay bloklang va 'Spam' tugmasini bosing.",
    "💳 <b>Bank kartasi ma'lumotlarini himoyalang!</b> Hech qachon bank kartangiz ustidagi to'liq raqamlarni, amal qilish muddatini va ayniqsa kartaning orqa tarafidagi 3 xonali CVV/CVC kodini begona shaxslarga bermang."
]


class TipsService:
    def get_random_tip(self) -> str:
        """Get a random cybersecurity tip from the list."""
        tip = random.choice(TIPS)
        return (
            "💡 <b>KUN MASLAHATI — KIBERXAVFSIZLIK MADANIYATI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{tip}\n\n"
            "🛡️ <i>O'zingiz va yaqinlaringizni kiber-tahdidlardan asrang!</i>"
        )
