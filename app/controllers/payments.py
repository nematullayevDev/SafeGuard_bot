"""Premium subscription manual card activation and billing controls."""
import logging
from datetime import datetime, timedelta
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.container import Container
from app.core.bot import bot
from app.core.config import settings
from app.repositories.base import get_conn
from app.states.states import AdminState
from app.views.keyboards import back_button

logger = logging.getLogger(__name__)

PREMIUM_PLANS = {
    "buy_3d": {"days": 3, "label": "3 kunlik"},
    "buy_7d": {"days": 7, "label": "1 haftalik"},
    "buy_30d": {"days": 30, "label": "1 oylik"},
    "buy_180d": {"days": 180, "label": "6 oylik"},
    "buy_365d": {"days": 365, "label": "1 yillik"},
}

async def get_owner_link(c: Container) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT username FROM users WHERE user_id = ?", (settings.admin_id,)).fetchone()
    if row and row[0]:
        uname = row[0].lstrip("@")
        return f"https://t.me/{uname}"
    return "https://t.me/webdragon"

def register(dp: Dispatcher, c: Container) -> None:

    async def cmd_premium(message: Message):
        uid = message.from_user.id
        lang = c.users.get_language(uid)
        plan = c.subscriptions.get_user_plan(uid)
        is_premium = plan["plan"] == "premium"
        expires_at = plan["expires_at"]
        
        status_text = {
            "uz": f"💎 <b>Premium Obuna:</b> Faol ✅ (Muddati: {expires_at})" if is_premium else "💎 <b>Premium Obuna:</b> Faolsiz ❌",
            "uz_cyr": f"💎 <b>Премиум Обуна:</b> Фаол ✅ (Муддати: {expires_at})" if is_premium else "💎 <b>Премиум Обуна:</b> Фаолсиз ❌",
            "ru": f"💎 <b>Премиум Подписка:</b> Активна ✅ (До: {expires_at})" if is_premium else "💎 <b>Премиум Подписка:</b> Неактивна ❌",
            "en": f"💎 <b>Premium Subscription:</b> Active ✅ (Expires: {expires_at})" if is_premium else "💎 <b>Premium Subscription:</b> Inactive ❌"
        }.get(lang, "")

        text = {
            "uz": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium afzalliklari:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Cheksiz AI tahlil:</b> Guruhlarda kiber-tahlil limiti kuniga 2000 tagacha oshadi!\n"
                "🔗 <b>Keshlanmagan skanerlash:</b> Havola va fayllarni chuqur tekshirish.\n"
                "📂 <b>Forensics Arxivi:</b> Qonunbuzarliklar haqida to'liq hisobotlar.\n"
                "👑 <b>Maxsus Nishon:</b> Profilingiz yonida 💎 nishoni aks etadi!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Premium faollashtirish karta orqali amalga oshiriladi.\n"
                "Quyidagi tugmani bosib administratorga to'lov haqida yozing."
            ),
            "uz_cyr": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium афзалликлари:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Чексиз AI таҳлил:</b> Гуруҳларда кибер-таҳлил лимити кунига 2000 тагача ошади!\n"
                "🔗 <b>Кешланмаган сканерлаш:</b> Ҳавола ва файлларни chuqur tekshirish.\n"
                "📂 <b>Forensics Архиви:</b> Қонунбузарликлар ҳақида тўлиқ ҳисоботлар.\n"
                "👑 <b>Махсус Нишон:</b> Профилингиз ёнида 💎 нишони акс этади!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Премиум фаоллаштириш karta orqali amalga oshiriladi.\n"
                "Қуйидаги tugmani bosib administratorga to'lov haqida yozing."
            ),
            "ru": (
                f"{status_text}\n\n"
                "<b>💎 Преимущества SafeGuard Premium:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Безлимитный ИИ-анализ:</b> Лимит ИИ-анализа в группах увеличивается до 2000 в день!\n"
                "🔗 <b>Глубокое сканирование:</b> Сканирование ссылок и файлов без задержек.\n"
                "📂 <b>Архив расследований:</b> Подробные отчеты об угрозах.\n"
                "👑 <b>Особый Знак:</b> Рядом с вашим профилем появится значок 💎!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Активация Premium производится через карту.\n"
                "Нажмите кнопку ниже, чтобы написать администратору об оплате."
            ),
            "en": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium Benefits:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Unlimited AI Analysis:</b> The group AI analysis limit increases to 2000 per day!\n"
                "🔗 <b>Deep Scanning:</b> Comprehensive checks for links and files.\n"
                "📂 <b>Forensics Archive:</b> Full security violation reports.\n"
                "👑 <b>Special Badge:</b> A 💎 badge will appear next to your profile!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Premium activation is done via manual card payment.\n"
                "Click the button below to contact the admin for payment details."
            )
        }.get(lang, "")

        owner_url = await get_owner_link(c)
        btn_pay = {
            "uz": "💳 Sotib olish (Lichka)",
            "uz_cyr": "💳 Сотиб олиш (Личка)",
            "ru": "💳 Купить (Личка)",
            "en": "💳 Purchase (Admin)"
        }.get(lang, "")

        back_btn_text = {
            "uz": "🔙 Orqaga",
            "uz_cyr": "🔙 Орқага",
            "ru": "🔙 Назад",
            "en": "🔙 Back"
        }.get(lang, "")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn_pay, url=owner_url)],
            [InlineKeyboardButton(text=back_btn_text, callback_data="main_menu")]
        ])

        await message.answer(text, reply_markup=kb, parse_mode="HTML")

    async def callback_premium(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        plan = c.subscriptions.get_user_plan(uid)
        is_premium = plan["plan"] == "premium"
        expires_at = plan["expires_at"]
        
        status_text = {
            "uz": f"💎 <b>Premium Obuna:</b> Faol ✅ (Muddati: {expires_at})" if is_premium else "💎 <b>Premium Obuna:</b> Faolsiz ❌",
            "uz_cyr": f"💎 <b>Премиум Обуна:</b> Фаол ✅ (Муддати: {expires_at})" if is_premium else "💎 <b>Премиум Обуна:</b> Фаолсиз ❌",
            "ru": f"💎 <b>Премиум Подписка:</b> Активна ✅ (До: {expires_at})" if is_premium else "💎 <b>Премиум Подписка:</b> Неактивна ❌",
            "en": f"💎 <b>Premium Subscription:</b> Active ✅ (Expires: {expires_at})" if is_premium else "💎 <b>Premium Subscription:</b> Inactive ❌"
        }.get(lang, "")

        text = {
            "uz": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium afzalliklari:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Cheksiz AI tahlil:</b> Guruhlarda kiber-tahlil limiti kuniga 2000 tagacha oshadi!\n"
                "🔗 <b>Keshlanmagan skanerlash:</b> Havola va fayllarni chuqur tekshirish.\n"
                "📂 <b>Forensics Arxivi:</b> Qonunbuzarliklar haqida to'liq hisobotlar.\n"
                "👑 <b>Maxsus Nishon:</b> Profilingiz yonida 💎 nishoni aks etadi!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Premium faollashtirish karta orqali amalga oshiriladi.\n"
                "Quyidagi tugmani bosib administratorga to'lov haqida yozing."
            ),
            "uz_cyr": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium афзалликлари:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Чексиз AI таҳлил:</b> Гуруҳларда кибер-таҳлил лимити кунига 2000 тагача ошади!\n"
                "🔗 <b>Кешланмаган сканерлаш:</b> Ҳавола ва файлларни chuqur tekshirish.\n"
                "📂 <b>Forensics Архиви:</b> Қонунбузарликлар ҳақида тўлиқ ҳисоботлар.\n"
                "👑 <b>Махсус Нишон:</b> Профилингиз ёнида 💎 нишони акс этади!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Премиум фаоллаштириш karta orqali amalga oshiriladi.\n"
                "Қуйидаги tugmani bosib administratorga to'lov haqida yozing."
            ),
            "ru": (
                f"{status_text}\n\n"
                "<b>💎 Преимущества SafeGuard Premium:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Безлимитный ИИ-анализ:</b> Лимит ИИ-анализа в группах увеличивается до 2000 в день!\n"
                "🔗 <b>Глубокое сканирование:</b> Сканирование ссылок и файлов без задержек.\n"
                "📂 <b>Архив расследований:</b> Подробные отчеты об угрозах.\n"
                "👑 <b>Особый Знак:</b> Рядом с вашим профилем появится значок 💎!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Активация Premium производится через карту.\n"
                "Нажмите кнопку ниже, чтобы написать администратору об оплате."
            ),
            "en": (
                f"{status_text}\n\n"
                "<b>💎 SafeGuard Premium Benefits:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 <b>Unlimited AI Analysis:</b> The group AI analysis limit increases to 2000 per day!\n"
                "🔗 <b>Deep Scanning:</b> Comprehensive checks for links and files.\n"
                "📂 <b>Forensics Archive:</b> Full security violation reports.\n"
                "👑 <b>Special Badge:</b> A 💎 badge will appear next to your profile!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💳 Premium activation is done via manual card payment.\n"
                "Click the button below to contact the admin for payment details."
            )
        }.get(lang, "")

        owner_url = await get_owner_link(c)
        btn_pay = {
            "uz": "💳 Sotib olish (Lichka)",
            "uz_cyr": "💳 Сотиб олиш (Личка)",
            "ru": "💳 Купить (Личка)",
            "en": "💳 Purchase (Admin)"
        }.get(lang, "")

        back_btn_text = {
            "uz": "🔙 Orqaga",
            "uz_cyr": "🔙 Орқага",
            "ru": "🔙 Назад",
            "en": "🔙 Back"
        }.get(lang, "")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn_pay, url=owner_url)],
            [InlineKeyboardButton(text=back_btn_text, callback_data="main_menu")]
        ])

        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await call.answer()

    # ---- ADMIN PREMIUM GIVING FLOW ----

    async def admin_start_premium_give(call: CallbackQuery, state: FSMContext):
        if call.from_user.id != settings.admin_id:
            await call.answer("Siz admin emassiz!", show_alert=True)
            return
            
        await call.message.edit_text(
            "💎 <b>Premium faollashtirish (Admin Panel)</b>\n\n"
            "Foydalanuvchini topish uchun uning:\n"
            "▫️ <b>Telegram User ID</b> (masalan: <code>123456789</code>)\n"
            "▫️ <b>Telefon raqami</b> (masalan: <code>+998901234567</code>)\n"
            "▫️ <b>Username</b> (masalan: <code>@webdragon</code>)\n\n"
            "tarkibini kiriting:",
            reply_markup=back_button("admin_panel", "uz"),
            parse_mode="HTML"
        )
        await state.set_state(AdminState.waiting_premium_user)
        await call.answer()

    async def admin_process_premium_user(message: Message, state: FSMContext):
        if message.from_user.id != settings.admin_id:
            return
            
        input_text = message.text.strip()
        user_row = None
        
        # Determine query type
        if input_text.isdigit():
            # User ID
            with get_conn() as conn:
                user_row = conn.execute("SELECT user_id, first_name, username, phone FROM users WHERE user_id = ?", (int(input_text),)).fetchone()
        elif input_text.startswith("+") or (len(input_text) >= 9 and input_text.replace(" ", "").isdigit()):
            # Phone number
            phone_clean = "+" + input_text.lstrip("+").replace(" ", "")
            phone_clean_no_plus = input_text.lstrip("+").replace(" ", "")
            with get_conn() as conn:
                user_row = conn.execute(
                    "SELECT user_id, first_name, username, phone FROM users WHERE phone = ? OR phone = ? OR phone LIKE ?",
                    (phone_clean, phone_clean_no_plus, f"%{phone_clean_no_plus}%")
                ).fetchone()
        else:
            # Username
            username_clean = input_text.lstrip("@").lower()
            with get_conn() as conn:
                user_row = conn.execute(
                    "SELECT user_id, first_name, username, phone FROM users WHERE LOWER(username) = ?",
                    (username_clean,)
                ).fetchone()

        if not user_row:
            await message.answer(
                "❌ <b>Foydalanuvchi topilmadi!</b>\n\n"
                "Iltimos, ma'lumotni to'g'ri kiritganingizga ishonch hosil qiling va qayta yozing, "
                "yoki bekor qilish uchun /cancel buyrug'ini yuboring.",
                parse_mode="HTML"
            )
            return

        target_id, target_name, target_username, target_phone = user_row
        await state.update_data(target_id=target_id, target_name=target_name)
        
        # Present duration options
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="3 kunlik (Test)", callback_data="give_buy_3d"),
                InlineKeyboardButton(text="1 haftalik", callback_data="give_buy_7d")
            ],
            [
                InlineKeyboardButton(text="1 oylik", callback_data="give_buy_30d"),
                InlineKeyboardButton(text="6 oylik", callback_data="give_buy_180d")
            ],
            [
                InlineKeyboardButton(text="1 yillik", callback_data="give_buy_365d")
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ])
        
        uname_str = f"@{target_username}" if target_username else "mavjud emas"
        phone_str = target_phone if target_phone else "mavjud emas"
        
        await message.answer(
            f"👤 <b>Foydalanuvchi topildi:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Ism:</b> {target_name}\n"
            f"<b>ID:</b> <code>{target_id}</code>\n"
            f"<b>Username:</b> {uname_str}\n"
            f"<b>Telefon:</b> {phone_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Quyidagi premium muddatlaridan birini tanlang:",
            reply_markup=kb,
            parse_mode="HTML"
        )

    async def admin_confirm_premium_give(call: CallbackQuery, state: FSMContext):
        if call.from_user.id != settings.admin_id:
            await call.answer("Ruxsat berilmagan!", show_alert=True)
            return
            
        plan_key = call.data.replace("give_", "")
        plan = PREMIUM_PLANS.get(plan_key)
        if not plan:
            await call.answer("Noma'lum reja.", show_alert=True)
            return
            
        data = await state.get_data()
        target_id = data.get("target_id")
        target_name = data.get("target_name")
        
        if not target_id:
            await call.answer("Foydalanuvchi ma'lumoti topilmadi.", show_alert=True)
            return
            
        # Activate Premium in database
        c.subscriptions.activate_user_premium(target_id, plan["days"], plan["label"])
        
        # Clear state
        await state.clear()
        
        # Notify Admin
        await call.message.edit_text(
            f"✅ <b>Premium obuna faollashtirildi!</b>\n\n"
            f"👤 Foydalanuvchi: {target_name} (ID: {target_id})\n"
            f"📅 Muddat: {plan['label']} ({plan['days']} kun)",
            reply_markup=back_button("admin_panel", "uz"),
            parse_mode="HTML"
        )
        
        # Notify User
        user_lang = c.users.get_language(target_id)
        expires_at = (datetime.now() + timedelta(days=plan["days"])).strftime("%Y-%m-%d %H:%M:%S")
        
        congrats_text = {
            "uz": (
                f"🎉 <b>Tabriklaymiz! SafeGuard Premium obunangiz faollashtirildi!</b>\n\n"
                f"📅 <b>Muddat:</b> {plan['label']} (Amal qilish muddati: {expires_at})\n\n"
                f"🚀 Endi sizda cheksiz kiber-tahlillar (kuniga 2000 ta AI), keshlanmagan havola/fayl tekshiruvlari "
                f"va profilingiz yonida maxsus 💎 nishoni faol bo'ldi!"
            ),
            "uz_cyr": (
                f"🎉 <b>Табриклаймиз! SafeGuard Премиум обунангиз фаоллаштирилди!</b>\n\n"
                f"📅 <b>Муддат:</b> {plan['label']} (Амал қилиш муддати: {expires_at})\n\n"
                f"🚀 Энди сизда чексиз кибер-таҳлиллар (кунига 2000 та AI), кешланмаган ҳавола/файл теширувлари "
                f"ва профилингиз ёнида махсус 💎 нишони фаол бўлди!"
            ),
            "ru": (
                f"🎉 <b>Поздравляем! Ваша подписка SafeGuard Premium успешно активирована!</b>\n\n"
                f"📅 <b>Период:</b> {plan['label']} (Действительна до: {expires_at})\n\n"
                f"🚀 Теперь вам доступны безлимитный анализ (2000 ИИ-проверок в день), прямое сканирование ссылок/файлов "
                f"без кэширования и специальный знак 💎 рядом с вашим профилем!"
            ),
            "en": (
                f"🎉 <b>Congratulations! Your SafeGuard Premium subscription is active!</b>\n\n"
                f"📅 <b>Duration:</b> {plan['label']} (Expires: {expires_at})\n\n"
                f"🚀 You now have unlimited cyber-analyses (2000 AI checks per day), deep link/file scans "
                f"and a premium 💎 badge next to your profile!"
            )
        }.get(user_lang, congrats_text["uz"])
        
        try:
            await bot.send_message(target_id, congrats_text, parse_mode="HTML")
        except Exception as e:
            logger.warning(f"Foydalanuvchiga premium xabari yuborilmadi: {e}")
            
        await call.answer()

    # Cancel command inside waiting state
    async def cancel_handler(message: Message, state: FSMContext):
        if message.from_user.id != settings.admin_id:
            return
        await state.clear()
        await message.answer("Bekor qilindi. Bosh menyuga qaytish uchun /start bosing.")

    # Register handlers
    dp.message.register(cmd_premium, Command("premium"))
    dp.callback_query.register(callback_premium, F.data == "open_premium")
    
    # Admin premium give registration
    dp.callback_query.register(admin_start_premium_give, F.data == "admin_premium_give")
    dp.message.register(cancel_handler, Command("cancel"), AdminState.waiting_premium_user)
    dp.message.register(admin_process_premium_user, AdminState.waiting_premium_user)
    dp.callback_query.register(admin_confirm_premium_give, F.data.startswith("give_buy_"))
