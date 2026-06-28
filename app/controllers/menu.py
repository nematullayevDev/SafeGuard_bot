"""Main menu and inline-keyboard callbacks (user-side + admin panel)."""
import logging

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.container import Container
from app.controllers.filters import deny_if_not_owner, is_owner
from app.core.config import PLATFORMS, settings
from app.views import formatters
from app.views.keyboards import (
    admin_banned_sites_kb, admin_panel_menu, back_button, blacklist_menu,
    group_mode_menu, groups_export_kb, main_menu, spam_filter_menu,
    users_export_kb, admin_stats_kb,
)
from app.views.texts import get_text

logger = logging.getLogger(__name__)


def register(dp: Dispatcher, c: Container) -> None:

    # ─── Navigation ──────────────────────────
    async def go_start(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        text = {
            "uz": "Iltimos /start buyrug'ini yuboring.",
            "uz_cyr": "Илтимос /start буйруғини юборинг.",
            "ru": "Пожалуйста, отправьте команду /start.",
            "en": "Please send the /start command."
        }.get(lang, "Iltimos /start")
        await call.message.answer(text)
        await call.answer()

    async def home(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        await call.message.edit_text(
            get_text("welcome", lang).format(name=call.from_user.first_name or "Foydalanuvchi"),
            reply_markup=main_menu(is_owner(call), lang),
            parse_mode="HTML",
        )
        await call.answer()

    # ─── Admin panel ─────────────────────────
    async def admin_panel(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        await call.message.edit_text(
            "👑 <b>Admin Paneli</b>\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=admin_panel_menu(), parse_mode="HTML",
        )
        await call.answer()

    async def admin_stats(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        await call.message.edit_text(
            formatters.stats_text(c.stats.get()),
            reply_markup=admin_stats_kb(), parse_mode="HTML",
        )
        await call.answer()

    async def admin_users(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        await call.message.edit_text(
            formatters.users_list(c.users.all()),
            parse_mode="HTML",
            reply_markup=users_export_kb(back_cb="admin_panel"),
        )
        await call.answer()

    async def admin_broadcast(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        await call.message.edit_text(
            "📢 <b>Broadcast</b>\n\n"
            "Barcha foydalanuvchilarga xabar yuborish uchun\n"
            "/broadcast buyrug'ini yuboring.",
            reply_markup=back_button("admin_panel"), parse_mode="HTML",
        )
        await call.answer()

    async def admin_groups(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        all_groups = c.groups.all()
        active = [g for g in all_groups if g.is_active]
        inactive = [g for g in all_groups if not g.is_active]

        if not all_groups:
            await call.message.edit_text(
                "🤖 <b>Bot qaysi guruhlarda</b>\n\n"
                "❗ Hali hech qanday guruhga qo'shilmagan.",
                reply_markup=back_button("admin_panel"), parse_mode="HTML",
            )
        else:
            await call.message.edit_text(
                formatters.groups_admin_list(active, inactive),
                reply_markup=groups_export_kb(back_cb="admin_panel"),
                parse_mode="HTML",
            )
        await call.answer()

    async def admin_banned_sites(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        counts = {p: c.banned_sites.count(p) for p in PLATFORMS}
        total = sum(counts.values())
        lines = ["🚫 <b>Taqiqlangan Saytlar Boshqaruvi</b>\n━━━━━━━━━━━━━━━━━━━━\n"]
        for pid, ptitle in PLATFORMS.items():
            lines.append(f"{ptitle}: <b>{counts[pid]}</b> ta")
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━\nJami: <b>{total}</b> ta")
        await call.message.edit_text(
            "\n".join(lines), reply_markup=admin_banned_sites_kb(), parse_mode="HTML",
        )
        await call.answer()

    # ─── Static info ─────────────────────────
    async def commands(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        user_cmds = {
            "uz": "📂 <b>Foydalanuvchi buyruqlari:</b>\n\n▫️ /start — Botni ishga tushirish\n▫️ /menu — Bosh menyuni ochish\n▫️ /lang — Tilni o'zgartirish\n",
            "uz_cyr": "📂 <b>Foydalanuvchi buyruqlari:</b>\n\n▫️ /start — Ботни ишга тушириш\n▫️ /menu — Бош менюни очиш\n▫️ /lang — Тилни ўзгартириш\n",
            "ru": "📂 <b>Команды пользователя:</b>\n\n▫️ /start — Запустить бота\n▫️ /menu — Открыть главное меню\n▫️ /lang — Изменить язык общения\n",
            "en": "📂 <b>User commands:</b>\n\n▫️ /start — Start the bot\n▫️ /menu — Open main menu\n▫️ /lang — Change language\n"
        }.get(lang, "")
        
        admin_cmds = ""
        if is_owner(call):
            admin_cmds = {
                "uz": "\n👑 <b>Admin buyruqlari:</b>\n\n▫️ /users — Foydalanuvchilar ro'yxati\n▫️ /stats — Bot statistikasi\n▫️ /broadcast — Xabar tarqatish\n",
                "uz_cyr": "\n👑 <b>Админ буйруқлари:</b>\n\n▫️ /users — Фойдаланувчилар рўйхати\n▫️ /stats — Бот статистикаси\n▫️ /broadcast — Хабар тарқатиш\n",
                "ru": "\n👑 <b>Команды админа:</b>\n\n▫️ /users — Список пользователей\n▫️ /stats — Статистика бота\n▫️ /broadcast — Рассылка сообщения\n",
                "en": "\n👑 <b>Admin commands:</b>\n\n▫️ /users — Users list\n▫️ /stats — Bot statistics\n▫️ /broadcast — Broadcast message\n"
            }.get(lang, "")

        group_cmds = {
            "uz": "\n👥 <b>Guruh buyruqlari (admin uchun):</b>\n\n▫️ /enable — Himoyani yoqish\n▫️ /disable — Himoyani o'chirish\n▫️ /status — Himoya holati\n▫️ /lang — Guruh tilini sozlash\n▫️ /warn — Foydalanuvchiga warn\n▫️ /warns — Warn sonini ko'rish\n▫️ /unwarn — Warnlarni tozalash\n",
            "uz_cyr": "\n👥 <b>Гуруҳ буйруқлари (админ учун):</b>\n\n▫️ /enable — Ҳимояни ёқиш\n▫️ /disable — Ҳимояни ўчириш\n▫️ /status — Ҳимоя ҳолати\n▫️ /lang — Гуруҳ тилини созлаш\n▫️ /warn — Фойдаланувчига warn\n▫️ /warns — Warn сонини кўриш\n▫️ /unwarn — Warnларни тозалаш\n",
            "ru": "\n👥 <b>Групповые команды (для админов):</b>\n\n▫️ /enable — Включить защиту\n▫️ /disable — Отключить защиту\n▫️ /status — Статус защиты\n▫️ /lang — Выбрать язык группы\n▫️ /warn — Дать предупреждение\n▫️ /warns — Проверить предупреждения\n▫️ /unwarn — Сбросить предупреждения\n",
            "en": "\n👥 <b>Group commands (for admins):</b>\n\n▫️ /enable — Enable protection\n▫️ /disable — Disable protection\n▫️ /status — Protection status\n▫️ /lang — Set group language\n▫️ /warn — Warn user\n▫️ /warns — View warning count\n▫️ /unwarn — Clear warnings\n"
        }.get(lang, "")

        await call.message.edit_text(
            user_cmds + admin_cmds + group_cmds,
            reply_markup=back_button("main_menu", lang), parse_mode="HTML",
        )
        await call.answer()

    async def help_view(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        help_text = {
            "uz": "🆘 Yordam:\n\n"
                  "🔗 Link yuboring — tekshiriladi\n"
                  "📦 APK/fayl yuboring — tahlil qilinadi\n\n"
                  "🚫 Spam Filter — shubhali matnlarni aniqlaydi\n"
                  "📋 Qora Ro'yxat — xavfli linklar ro'yxati\n"
                  "📊 Tarixim — oxirgi tekshiruvlar\n"
                  "👥 Guruh Rejimi — guruhni himoya qilish\n"
                  "🌐 Taqiqlangan Saytlar — O'zbekistonda taqiqlangan kontent\n\n"
                  f"⚡ <b>Rate limit:</b> {settings.rate_limit_max} ta so'rov / {settings.rate_limit_window} sekund",
            "uz_cyr": "🆘 Ёрдам:\n\n"
                      "🔗 Линк юборинг — текширилади\n"
                      "📦 APK/файл юборинг — таҳлил қилинади\n\n"
                      "🚫 Спам Фильтр — шубҳали матнларни аниқлайди\n"
                      "📋 Қора Рўйхат — хавфли линклар рўйхати\n"
                      "📊 Тарихим — охирги текширувлар\n"
                      "👥 Гуруҳ Режими — гуруҳни ҳимоя қилиш\n"
                      "🌐 Тақиқланган Сайтлар — Ўзбекистонда тақиқланган контент\n\n"
                      f"⚡ <b>Rate limit:</b> {settings.rate_limit_max} та сўров / {settings.rate_limit_window} секунд",
            "ru": "🆘 Помощь:\n\n"
                  "🔗 Отправьте ссылку — бот ее проверит\n"
                  "📦 Отправьте APK/файл — бот проанализирует его\n\n"
                  "🚫 Спам Фильтр — определяет подозрительные тексты\n"
                  "📋 Черный Список — список вредоносных ссылок\n"
                  "📊 Моя История — ваши последние проверки\n"
                  "👥 Режим Групп — защита вашей группы\n"
                  "🌐 Запрещенные Сайты — ресурсы, заблокированные в Узбекистане\n\n"
                  f"⚡ <b>Лимит запросов:</b> {settings.rate_limit_max} запросов / {settings.rate_limit_window} сек",
            "en": "🆘 Help:\n\n"
                  "🔗 Send a link — it will be scanned\n"
                  "📦 Send an APK/file — it will be analyzed\n\n"
                  "🚫 Spam Filter — detects suspicious text patterns\n"
                  "📋 Blacklist — list of dangerous links\n"
                  "📊 My History — your recent scans\n"
                  "👥 Group Mode — protect your groups\n"
                  "🌐 Banned Sites — restricted content list in Uzbekistan\n\n"
                  f"⚡ <b>Rate limit:</b> {settings.rate_limit_max} requests / {settings.rate_limit_window} seconds"
        }.get(lang, "")
        await call.message.edit_text(
            help_text,
            reply_markup=back_button("main_menu", lang), parse_mode="HTML",
        )
        await call.answer()

    # ─── Spam filter ─────────────────────────
    async def spam_filter_view(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        is_on = c.user_settings.get_spam_filter(uid)
        
        status_on = {"uz": "Yoqiq", "uz_cyr": "Ёқиқ", "ru": "Включен", "en": "Enabled"}.get(lang, "Yoqiq")
        status_off = {"uz": "O'chiq", "uz_cyr": "Ўчиқ", "ru": "Выключен", "en": "Disabled"}.get(lang, "O'chiq")
        status_text = f"✅ {status_on}" if is_on else f"❌ {status_off}"
        
        title = {"uz": "🚫 Spam Filter\n\nHolat: ", "uz_cyr": "🚫 Спам Фильтр\n\nҲолат: ", "ru": "🚫 Спам Фильтр\n\nСтатус: ", "en": "🚫 Spam Filter\n\nStatus: "}.get(lang, "")
        
        await call.message.edit_text(
            f"{title}{status_text}",
            reply_markup=spam_filter_menu(is_on, lang),
        )
        await call.answer()

    async def spam_on(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        c.user_settings.set_spam_filter(uid, True)
        
        confirm = {"uz": "🚫 Spam Filter — ✅ Yoqildi!", "uz_cyr": "🚫 Спам Фильтр — ✅ Ёқилди!", "ru": "🚫 Спам Фильтр — ✅ Включен!", "en": "🚫 Spam Filter — ✅ Enabled!"}.get(lang, "")
        await call.message.edit_text(
            confirm, reply_markup=spam_filter_menu(True, lang)
        )
        await call.answer()

    async def spam_off(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        c.user_settings.set_spam_filter(uid, False)
        
        confirm = {"uz": "🚫 Spam Filter — ❌ O'chirildi.", "uz_cyr": "🚫 Спам Фильтр — ❌ Ўчирилди.", "ru": "🚫 Спам Фильтр — ❌ Отключен.", "en": "🚫 Spam Filter — ❌ Disabled."}.get(lang, "")
        await call.message.edit_text(
            confirm, reply_markup=spam_filter_menu(False, lang)
        )
        await call.answer()

    # ─── Blacklist ───────────────────────────
    async def blacklist(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        _, count = c.blacklist.recent()
        
        title = {
            "uz": f"📋 <b>Qora Ro'yxat</b>\n\nHozirda <b>{count}</b> ta yozuv bor.",
            "uz_cyr": f"📋 <b>Қора Рўйхат</b>\n\nHозирда <b>{count}</b> та ёзув бор.",
            "ru": f"📋 <b>Черный Список</b>\n\nНа данный момент записей: <b>{count}</b>.",
            "en": f"📋 <b>Blacklist</b>\n\nCurrently, there are <b>{count}</b> entries."
        }.get(lang, "")
        await call.message.edit_text(
            title,
            reply_markup=blacklist_menu(is_owner(call), lang),
            parse_mode="HTML",
        )
        await call.answer()

    async def bl_show(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        rows, count = c.blacklist.recent()
        await call.message.edit_text(
            formatters.blacklist_view(rows, count),
            reply_markup=blacklist_menu(is_owner(call), lang),
            parse_mode="HTML",
        )
        await call.answer()

    async def bl_clear(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        c.blacklist.clear()
        
        confirm = {"uz": "🗑 Qora ro'yxat tozalandi!", "uz_cyr": "🗑 Қора рўйхат тозаланди!", "ru": "🗑 Черный список очищен!", "en": "🗑 Blacklist cleared!"}.get(lang, "")
        await call.message.edit_text(confirm, reply_markup=blacklist_menu(is_owner(call), lang), parse_mode="HTML")
        await call.answer()

    # ─── History ─────────────────────────────
    async def history_view(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        entries = c.scanner.history(uid)
        await call.message.edit_text(
            formatters.history_list(entries), reply_markup=back_button("main_menu", lang),
        )
        await call.answer()

    # ─── Group mode toggle (per-chat) ────────
    async def group_mode_view(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        chat_id = call.message.chat.id
        is_on = c.user_settings.get_group_mode(chat_id)
        active = len(c.groups.active())
        
        status_on = {"uz": "Yoqiq", "uz_cyr": "Ёқиқ", "ru": "Включен", "en": "Enabled"}.get(lang, "Yoqiq")
        status_off = {"uz": "O'chiq", "uz_cyr": "Ўчиқ", "ru": "Выключен", "en": "Disabled"}.get(lang, "O'chiq")
        status_text = f"✅ {status_on}" if is_on else f"❌ {status_off}"
        
        desc = {
            "uz": "👥 Guruh Rejimi\n\nXavfli link → xabar o'chiriladi + ogohlantirish + warn\n3 ta warn → foydalanuvchi ban\n\n"
                  f"📌 Qo'shilgan guruhlar: <b>{active}</b> ta\n"
                  f"Holat: {status_text}",
            "uz_cyr": "👥 Гуруҳ Режими\n\nХавфли линк → хабар ўчирилади + огоҳлантириш + warn\n3 та warn → фойдаланувчи ban\n\n"
                      f"📌 Қўшилган гуруҳлар: <b>{active}</b> та\n"
                      f"Ҳолат: {status_text}",
            "ru": "👥 Режим Групп\n\nВредоносная ссылка → удаление сообщения + предупреждение + warn\n3 варна → бан пользователя\n\n"
                  f"📌 Добавленные группы: <b>{active}</b>\n"
                  f"Статус: {status_text}",
            "en": "👥 Group Mode\n\nMalicious link → message deleted + warning + warn\n3 warns → user ban\n\n"
                  f"📌 Added groups: <b>{active}</b>\n"
                  f"Status: {status_text}"
        }.get(lang, "")
        
        await call.message.edit_text(
            desc,
            reply_markup=group_mode_menu(is_on, lang), parse_mode="HTML",
        )
        await call.answer()

    async def gm_on(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        c.user_settings.set_group_mode(call.message.chat.id, True)
        active = len(c.groups.active())
        
        confirm = {
            "uz": f"👥 Guruh Rejimi — ✅ Yoqildi!\n\n📌 Qo'shilgan guruhlar: <b>{active}</b> ta",
            "uz_cyr": f"👥 Гуруҳ Режими — ✅ Ёқилди!\n\n📌 Қўшилган гуруҳлар: <b>{active}</b> та",
            "ru": f"👥 Режим Групп — ✅ Включен!\n\n📌 Добавленные группы: <b>{active}</b>",
            "en": f"👥 Group Mode — ✅ Enabled!\n\n📌 Added groups: <b>{active}</b>"
        }.get(lang, "")
        await call.message.edit_text(
            confirm, reply_markup=group_mode_menu(True, lang), parse_mode="HTML",
        )
        await call.answer()

    async def gm_off(call: CallbackQuery):
        uid = call.from_user.id
        lang = c.users.get_language(uid)
        c.user_settings.set_group_mode(call.message.chat.id, False)
        active = len(c.groups.active())
        
        confirm = {
            "uz": f"👥 Guruh Rejimi — ❌ O'chirildi.\n\n📌 Qo'shilgan guruhlar: <b>{active}</b> ta",
            "uz_cyr": f"👥 Гуруҳ Режими — ❌ Ўчирилди.\n\n📌 Қўшилган гуруҳлар: <b>{active}</b> та",
            "ru": f"👥 Режим Групп — ❌ Отключен.\n\n📌 Добавленные группы: <b>{active}</b>",
            "en": f"👥 Group Mode — ❌ Disabled.\n\n📌 Added groups: <b>{active}</b>"
        }.get(lang, "")
        await call.message.edit_text(
            confirm, reply_markup=group_mode_menu(False, lang), parse_mode="HTML",
        )
        await call.answer()

    async def gm_list(call: CallbackQuery):
        user_id = call.from_user.id
        lang = c.users.get_language(user_id)
        my_groups = c.groups.active_by_user(user_id)
        if not my_groups:
            text = {
                "uz": "📋 <b>Mening guruhlarim</b>\n\n❗ Siz hali hech qanday guruhga bot qo'shmagansiz.\n\n➕ <i>«Guruhga qo'shish»</i> tugmasini bosib botni guruhingizga qo'shing!",
                "uz_cyr": "📋 <b>Менинг гуруҳларим</b>\n\n❗ Сиз ҳали ҳеч қандай гуруҳга бот қўшмагансиз.\n\n➕ <i>«Гуруҳга қўшиш»</i> тугмасини босиб ботни гуруҳингизга қўшинг!",
                "ru": "📋 <b>Мои группы</b>\n\n❗ Вы еще не добавили бот ни в одну группу.\n\n➕ Нажмите кнопку <i>«Добавить в группу»</i>, чтобы добавить бота!",
                "en": "📋 <b>My groups</b>\n\n❗ You haven't added the bot to any groups yet.\n\n➕ Click the <i>«Add to group»</i> button to invite the bot!"
            }.get(lang, "")
            
            back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "Back")
            await call.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=back_lbl, callback_data="group_mode")]
                ]),
                parse_mode="HTML",
            )
        else:
            await call.message.edit_text(
                formatters.groups_user_list(my_groups),
                reply_markup=groups_export_kb(back_cb="group_mode"),
                parse_mode="HTML",
            )
        await call.answer()

    # Registrations
    dp.callback_query.register(go_start, F.data == "go_start")
    dp.callback_query.register(home, F.data == "main_menu")

    dp.callback_query.register(admin_panel, F.data == "admin_panel")
    dp.callback_query.register(admin_stats, F.data == "admin_stats")
    dp.callback_query.register(admin_users, F.data == "admin_users")
    dp.callback_query.register(admin_broadcast, F.data == "admin_broadcast")
    dp.callback_query.register(admin_groups, F.data == "admin_groups")
    dp.callback_query.register(admin_banned_sites, F.data == "admin_banned_sites")

    dp.callback_query.register(commands, F.data == "commands")
    dp.callback_query.register(help_view, F.data == "help")

    dp.callback_query.register(spam_filter_view, F.data == "spam_filter")
    dp.callback_query.register(spam_on, F.data == "spam_on")
    dp.callback_query.register(spam_off, F.data == "spam_off")

    dp.callback_query.register(blacklist, F.data == "blacklist")
    dp.callback_query.register(bl_show, F.data == "bl_show")
    dp.callback_query.register(bl_clear, F.data == "bl_clear")

    dp.callback_query.register(history_view, F.data == "history")

    dp.callback_query.register(group_mode_view, F.data == "group_mode")
    dp.callback_query.register(gm_on, F.data == "gm_on")
    dp.callback_query.register(gm_off, F.data == "gm_off")
    dp.callback_query.register(gm_list, F.data == "gm_list")
