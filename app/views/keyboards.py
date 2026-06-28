"""Inline and reply keyboards."""
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
)

from app.core.config import PLATFORMS, settings


def phone_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    text = {
        "uz": "📱 Raqamimni ulashish",
        "uz_cyr": "📱 Рақамимни улашиш",
        "ru": "📱 Поделиться контактом",
        "en": "📱 Share contact"
    }.get(lang, "📱 Raqamimni ulashish")
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def language_selection_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data="setlang_uz"),
            InlineKeyboardButton(text="Ўзбекча (Крил) 🇺🇿", callback_data="setlang_uz_cyr")
        ],
        [
            InlineKeyboardButton(text="Русский 🇷🇺", callback_data="setlang_ru"),
            InlineKeyboardButton(text="English 🇬🇧", callback_data="setlang_en")
        ]
    ])


def group_language_selection_kb(chat_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "Back")
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data=f"gset_setlang_{chat_id}_uz"),
            InlineKeyboardButton(text="Ўзбекча (Крил) 🇺🇿", callback_data=f"gset_setlang_{chat_id}_uz_cyr")
        ],
        [
            InlineKeyboardButton(text="Русский 🇷🇺", callback_data=f"gset_setlang_{chat_id}_ru"),
            InlineKeyboardButton(text="English 🇬🇧", callback_data=f"gset_setlang_{chat_id}_en")
        ],
        [
            InlineKeyboardButton(text=back_lbl, callback_data=f"group_settings_back_{chat_id}")
        ]
    ])


def main_menu(is_admin_user: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    btn_spam = {"uz": "🚫 Spam Filter", "uz_cyr": "🚫 Спам Фильтр", "ru": "🚫 Спам Фильтр", "en": "🚫 Spam Filter"}.get(lang, "🚫 Spam Filter")
    btn_blacklist = {"uz": "📋 Qora Ro'yxat", "uz_cyr": "📋 Қора Рўйхат", "ru": "📋 Черный Список", "en": "📋 Blacklist"}.get(lang, "📋 Blacklist")
    btn_history = {"uz": "📊 Tarixim", "uz_cyr": "📊 Тарихим", "ru": "📊 Моя История", "en": "📊 My History"}.get(lang, "📊 My History")
    btn_group = {"uz": "👥 Guruh Rejimi", "uz_cyr": "👥 Гуруҳ Режими", "ru": "👥 Режим Групп", "en": "👥 Group Mode"}.get(lang, "👥 Group Mode")
    btn_ai = {"uz": "🤖 AI Maslahatchi", "uz_cyr": "🤖 AI Маслаҳатчи", "ru": "🤖 ИИ-Консультант", "en": "🤖 AI Consultant"}.get(lang, "🤖 AI Consultant")
    btn_banned = {"uz": "🌐 Taqiqlangan Saytlar", "uz_cyr": "🌐 Тақиқланган Сайтлар", "ru": "🌐 Запрещенные Сайты", "en": "🌐 Banned Sites"}.get(lang, "🌐 Banned Sites")
    btn_quiz = {"uz": "🛡️ Kiber-Viktorina", "uz_cyr": "🛡️ Кибер-Викторина", "ru": "🛡️ Кибер-Викторина", "en": "🛡️ Cyber-Quiz"}.get(lang, "🛡️ Cyber-Quiz")
    btn_commands = {"uz": "📂 Buyruqlar", "uz_cyr": "📂 Буйруқлар", "ru": "📂 Команды", "en": "📂 Commands"}.get(lang, "📂 Commands")
    btn_help = {"uz": "ℹ️ Yordam", "uz_cyr": "ℹ️ Ёрдам", "ru": "ℹ️ Помощь", "en": "ℹ️ Help"}.get(lang, "ℹ️ Help")
    btn_lang = {"uz": "🌐 Tilni o'zgartirish", "uz_cyr": "🌐 Тилни ўзгартириш", "ru": "🌐 Сменить язык", "en": "🌐 Change language"}.get(lang, "🌐 Change language")
    btn_admin = {"uz": "👑 Admin Paneli", "uz_cyr": "👑 Админ Панели", "ru": "👑 Панель Админа", "en": "👑 Admin Panel"}.get(lang, "👑 Admin Panel")

    rows = [
        [
            InlineKeyboardButton(text=btn_spam, callback_data="spam_filter"),
            InlineKeyboardButton(text=btn_blacklist, callback_data="blacklist"),
        ],
        [
            InlineKeyboardButton(text=btn_history, callback_data="history"),
            InlineKeyboardButton(text=btn_group, callback_data="group_mode"),
        ],
        [
            InlineKeyboardButton(text=btn_ai, callback_data="ai_assistant"),
            InlineKeyboardButton(text=btn_banned, callback_data="banned_sites_main"),
        ],
        [
            InlineKeyboardButton(text=btn_quiz, callback_data="quiz_main"),
            InlineKeyboardButton(text=btn_commands, callback_data="commands"),
        ],
        [
            InlineKeyboardButton(text=btn_help, callback_data="help"),
            InlineKeyboardButton(text=btn_lang, callback_data="change_language_private"),
        ],
    ]
    if is_admin_user:
        rows.append([InlineKeyboardButton(text=btn_admin, callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_panel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="🏛 Davlat Integratsiyasi", callback_data="admin_state_sync"),
            InlineKeyboardButton(text="📂 Kiber-Tergov", callback_data="admin_forensics_main"),
        ],
        [InlineKeyboardButton(text="🤖 Bot qaysi guruhlarda", callback_data="admin_groups")],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="💾 Baza Zaxirasi", callback_data="admin_backup"),
        ],
        [InlineKeyboardButton(text="🚫 Taqiqlangan Saytlar", callback_data="admin_banned_sites")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


def forensics_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚨 Ekstremizm", callback_data="admin_forensics_list_p0_cextremism"),
            InlineKeyboardButton(text="💊 Giyohvandlik", callback_data="admin_forensics_list_p0_cdrugs"),
        ],
        [
            InlineKeyboardButton(text="⚠️ Kiberbulling", callback_data="admin_forensics_list_p0_cbullying"),
            InlineKeyboardButton(text="💻 Kiberjinoyat", callback_data="admin_forensics_list_p0_ccybercrime"),
        ],
        [
            InlineKeyboardButton(text="🌐 Barchasi", callback_data="admin_forensics_list_p0_call"),
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")
        ],
    ])


def back_button(to: str = "main_menu", lang: str = "uz") -> InlineKeyboardMarkup:
    text = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=to)]
    ])


def spam_filter_menu(is_on: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    status_on = {"uz": "Yoqiq", "uz_cyr": "Ёқиқ", "ru": "Включен", "en": "Enabled"}.get(lang, "Yoqiq")
    status_off = {"uz": "O'chiq", "uz_cyr": "Ўчиқ", "ru": "Выключен", "en": "Disabled"}.get(lang, "O'chiq")
    lbl_status = {"uz": "Holat", "uz_cyr": "Ҳолат", "ru": "Статус", "en": "Status"}.get(lang, "Holat")
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    
    status = f"✅ {status_on}" if is_on else f"❌ {status_off}"
    toggle = "spam_off" if is_on else "spam_on"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{lbl_status}: {status}", callback_data=toggle)],
        [InlineKeyboardButton(text=back_lbl, callback_data="main_menu")],
    ])


def blacklist_menu(is_admin_user: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    btn_show = {"uz": "📋 Tekshirilgan linklar", "uz_cyr": "📋 Текширилган линклар", "ru": "📋 Проверенные ссылки", "en": "📋 Checked links"}.get(lang, "📋 Checked links")
    btn_clear = {"uz": "🗑 Tozalash (admin)", "uz_cyr": "🗑 Тозалаш (админ)", "ru": "🗑 Очистить (админ)", "en": "🗑 Clear (admin)"}.get(lang, "🗑 Clear (admin)")
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    
    rows = [
        [InlineKeyboardButton(text=btn_show, callback_data="bl_show")],
    ]
    if is_admin_user:
        rows.append([InlineKeyboardButton(text=btn_clear, callback_data="bl_clear")])
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _platform_grid(prefix: str, back_to: str, lang: str = "uz") -> InlineKeyboardMarkup:
    rows = []
    items = list(PLATFORMS.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(text=items[i][1], callback_data=f"{prefix}{items[i][0]}")]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(
                text=items[i + 1][1], callback_data=f"{prefix}{items[i + 1][0]}"
            ))
        rows.append(row)
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data=back_to)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def banned_sites_menu(lang: str = "uz") -> InlineKeyboardMarkup:
    return _platform_grid("bs_", "main_menu", lang)


def admin_add_site_platforms_menu() -> InlineKeyboardMarkup:
    return _platform_grid("addsite_", "admin_banned_sites")


def group_mode_menu(is_on: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    status_on = {"uz": "Yoqiq", "uz_cyr": "Ёқиқ", "ru": "Включен", "en": "Enabled"}.get(lang, "Yoqiq")
    status_off = {"uz": "O'chiq", "uz_cyr": "Ўчиқ", "ru": "Выключен", "en": "Disabled"}.get(lang, "O'chiq")
    lbl_status = {"uz": "Holat", "uz_cyr": "Ҳолат", "ru": "Статус", "en": "Status"}.get(lang, "Holat")
    btn_mygroups = {"uz": "📋 Guruhlarim", "uz_cyr": "📋 Гуруҳларим", "ru": "📋 Мои группы", "en": "📋 My groups"}.get(lang, "📋 My groups")
    btn_addgroup = {"uz": "➕ Guruhga qo'shish", "uz_cyr": "➕ Гуруҳга қўшиш", "ru": "➕ Добавить в группу", "en": "➕ Add to group"}.get(lang, "➕ Add to group")
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    
    status = f"✅ {status_on}" if is_on else f"❌ {status_off}"
    toggle = "gm_off" if is_on else "gm_on"
    bot_username = settings.bot_username.lstrip("@")
    add_url = (
        f"https://t.me/{bot_username}"
        "?startgroup=true&admin=delete_messages+restrict_members+ban_users+invite_users+change_info"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{lbl_status}: {status}", callback_data=toggle)],
        [InlineKeyboardButton(text=btn_mygroups, callback_data="gm_list")],
        [InlineKeyboardButton(text=btn_addgroup, url=add_url)],
        [InlineKeyboardButton(text=back_lbl, callback_data="main_menu")],
    ])


def users_export_kb(back_cb: str | None = None) -> InlineKeyboardMarkup:
    rows = [[
        InlineKeyboardButton(text="📄 PDF", callback_data="export_pdf"),
        InlineKeyboardButton(text="📝 DOCX", callback_data="export_docx"),
    ]]
    if back_cb:
        rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def groups_export_kb(back_cb: str | None = None) -> InlineKeyboardMarkup:
    rows = [[
        InlineKeyboardButton(text="📄 PDF yuklab olish", callback_data="groups_export_pdf"),
        InlineKeyboardButton(text="📝 DOCX yuklab olish", callback_data="groups_export_docx"),
    ]]
    if back_cb:
        rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def banned_detail_kb(platform: str, *, has_prev: bool, has_next: bool,
                      page: int, is_admin_user: bool) -> InlineKeyboardMarkup:
    rows = [[
        InlineKeyboardButton(text="📄 PDF", callback_data=f"bsexp_pdf_{platform}"),
        InlineKeyboardButton(text="📝 DOCX", callback_data=f"bsexp_docx_{platform}"),
    ]]
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(
            text="◀️ Oldingi", callback_data=f"bs_{platform}_p{page - 1}"
        ))
    if has_next:
        nav.append(InlineKeyboardButton(
            text="Keyingi ▶️", callback_data=f"bs_{platform}_p{page + 1}"
        ))
    if nav:
        rows.append(nav)
    if is_admin_user:
        rows.append([InlineKeyboardButton(
            text="🗑 Sayt o'chirish", callback_data=f"bsdel_list_{platform}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="banned_sites_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def banned_empty_kb(platform: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 PDF", callback_data=f"bsexp_pdf_{platform}"),
            InlineKeyboardButton(text="📝 DOCX", callback_data=f"bsexp_docx_{platform}"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="banned_sites_main")],
    ])


def admin_banned_sites_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi sayt qo'shish", callback_data="admin_add_site")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")],
    ])


def after_addsite_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="admin_add_site")],
        [InlineKeyboardButton(text="👑 Admin Paneli", callback_data="admin_panel")],
    ])


def go_start_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    text = {
        "uz": "📱 Ro'yxatdan o'tish",
        "uz_cyr": "📱 Рўйхатдан ўтиш",
        "ru": "📱 Зарегистрироваться",
        "en": "📱 Register"
    }.get(lang, "📱 Ro'yxatdan o'tish")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="go_start")]
    ])


def forensics_list_kb(suspects, page: int, has_prev: bool, has_next: bool, category: str = "all") -> InlineKeyboardMarkup:
    rows = []
    
    # 1. Suspects' names as buttons (one button per row)
    for s in suspects:
        name = s["full_name"].strip() if s.get("full_name") and s["full_name"].strip() not in (".", "") else f"Gumondor #{s['user_id']}"
        count = s.get("case_count", 1)
        if count > 1:
            name_text = f"{name} 🔄 ({count} ta)"
        else:
            name_text = f"{name} ({count} ta)"
            
        short_name = name_text[:28] + "..." if len(name_text) > 28 else name_text
        rows.append([InlineKeyboardButton(
            text=f"👤 {short_name}",
            callback_data=f"forensic_suspect_{s['user_id']}_p{page}_c{category}"
        )])
        
    # 2. Navigation Buttons (Always visible!)
    prev_cb = f"admin_forensics_list_p{page - 1}_c{category}" if has_prev else "dummy"
    next_cb = f"admin_forensics_list_p{page + 1}_c{category}" if has_next else "dummy"
    
    rows.append([
        InlineKeyboardButton(text="◀️ Oldingi", callback_data=prev_cb),
        InlineKeyboardButton(text="Keyingi ▶️", callback_data=next_cb)
    ])
        
    # 3. Bulk Export Buttons
    rows.append([
        InlineKeyboardButton(text="📥 PDF Yuklab olish", callback_data=f"forensiclist_pdf_{category}"),
        InlineKeyboardButton(text="📥 DOCX Yuklab olish", callback_data=f"forensiclist_docx_{category}")
    ])
        
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_forensics_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def forensic_detail_kb(user_id: int, page: int, category: str = "all") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 PDF Tergov Bayonnomasi", callback_data=f"forensic_pdf_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="📝 Word Tergov Bayonnomasi", callback_data=f"forensic_docx_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="🗑 Gumondorni o'chirish", callback_data=f"forensic_del_{user_id}_p{page}_c{category}"),
        ],
        [InlineKeyboardButton(text="🔙 Ro'yxatga orqaga", callback_data=f"admin_forensics_list_p{page}_c{category}")],
    ])


def group_settings_kb(chat_id: int, filters: dict, g_settings: dict, lang: str = "uz") -> InlineKeyboardMarkup:
    active_lbl = {"uz": "Faol", "uz_cyr": "Фаол", "ru": "Активен", "en": "Active"}
    inactive_lbl = {"uz": "O'chirilgan", "uz_cyr": "Ўчирилган", "ru": "Отключен", "en": "Disabled"}
    
    status_on = active_lbl.get(lang, "Faol")
    status_off = inactive_lbl.get(lang, "O'chirilgan")
    
    l_status = f"✅ {status_on}" if filters.get("filter_links", True) else f"❌ {status_off}"
    f_status = f"✅ {status_on}" if filters.get("filter_files", True) else f"❌ {status_off}"
    n_status = f"✅ {status_on}" if filters.get("filter_nlp", True) else f"❌ {status_off}"
    
    limit = g_settings.get("warnings_limit", 3)
    lang_code = g_settings.get("language", "uz")
    
    lang_names = {
        "uz": "O'zbekcha 🇺🇿",
        "uz_cyr": "Ўзбек (Крил) 🇺🇿",
        "ru": "Русский 🇷🇺",
        "en": "English 🇬🇧"
    }
    lang_name = lang_names.get(lang_code, "O'zbekcha 🇺🇿")

    lbl_links = {"uz": "🔗 Havolalar (Links)", "uz_cyr": "🔗 Ҳаволалар (Links)", "ru": "🔗 Ссылки (Links)", "en": "🔗 Links"}.get(lang, "🔗 Links")
    lbl_files = {"uz": "📦 Fayllar (Files/Viruses)", "uz_cyr": "📦 Файллар (Files/Viruses)", "ru": "📦 Файлы (Files/Viruses)", "en": "📦 Files"}.get(lang, "📦 Files")
    lbl_nlp = {"uz": "🧠 Matn Tahlili (NLP)", "uz_cyr": "🧠 Матн Таҳлили (NLP)", "ru": "🧠 Анализ Текста (NLP)", "en": "🧠 Text Analysis"}.get(lang, "🧠 Text Analysis")
    
    btn_warn_dec = {"uz": "➖ Warn", "uz_cyr": "➖ Warn", "ru": "➖ Warn", "en": "➖ Warn"}.get(lang, "➖ Warn")
    btn_warn_limit = {"uz": f"⚠️ Limit: {limit}", "uz_cyr": f"⚠️ Лимит: {limit}", "ru": f"⚠️ Лимит: {limit}", "en": f"⚠️ Limit: {limit}"}.get(lang, f"⚠️ Limit: {limit}")
    btn_warn_inc = {"uz": "➕ Warn", "uz_cyr": "➕ Warn", "ru": "➕ Warn", "en": "➕ Warn"}.get(lang, "➕ Warn")
    
    btn_kws = {"uz": "🚫 Kalit so'zlar", "uz_cyr": "🚫 Калит сўзлар", "ru": "🚫 Ключевые слова", "en": "🚫 Keywords"}.get(lang, "🚫 Keywords")
    btn_wl = {"uz": "✅ Oq ro'yxat", "uz_cyr": "✅ Оқ рўйхат", "ru": "✅ Белый список", "en": "✅ Whitelist"}.get(lang, "✅ Whitelist")
    btn_close = {"uz": "❌ Yopish", "uz_cyr": "❌ Ёпиш", "ru": "❌ Закрыть", "en": "❌ Close"}.get(lang, "❌ Close")

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=lbl_links, callback_data="dummy"),
            InlineKeyboardButton(text=l_status, callback_data=f"toggle_gset_{chat_id}_filter_links")
        ],
        [
            InlineKeyboardButton(text=lbl_files, callback_data="dummy"),
            InlineKeyboardButton(text=f_status, callback_data=f"toggle_gset_{chat_id}_filter_files")
        ],
        [
            InlineKeyboardButton(text=lbl_nlp, callback_data="dummy"),
            InlineKeyboardButton(text=n_status, callback_data=f"toggle_gset_{chat_id}_filter_nlp")
        ],
        # Warn limit adjustment row
        [
            InlineKeyboardButton(text=btn_warn_dec, callback_data=f"gset_warn_dec_{chat_id}"),
            InlineKeyboardButton(text=btn_warn_limit, callback_data="dummy"),
            InlineKeyboardButton(text=btn_warn_inc, callback_data=f"gset_warn_inc_{chat_id}")
        ],
        # Language switcher row
        [
            InlineKeyboardButton(text="🌐 Til (Language)", callback_data="dummy"),
            InlineKeyboardButton(text=lang_name, callback_data=f"gset_lang_menu_{chat_id}")
        ],
        # Custom Blacklist and Whitelist domain buttons
        [
            InlineKeyboardButton(text=btn_kws, callback_data=f"gset_edit_kws_{chat_id}"),
            InlineKeyboardButton(text=btn_wl, callback_data=f"gset_edit_wl_{chat_id}")
        ],
        [InlineKeyboardButton(text=btn_close, callback_data="close_group_settings")]
    ])


def admin_stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 PDF Hisobot Yuklash", callback_data="admin_stats_pdf")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ])


def quiz_main_menu(quiz_passed: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    status_passed = {
        "uz": "🎉 Testdan O'tgansiz (Qayta topshirish)",
        "uz_cyr": "🎉 Тестдан Ўтгансиз (Қайта топшириш)",
        "ru": "🎉 Тест Сдан (Пройти заново)",
        "en": "🎉 Test Passed (Retake)"
    }.get(lang, "🎉 Test Passed")
    
    status_start = {
        "uz": "📝 Testni Boshlash",
        "uz_cyr": "📝 Тестни Бошлаш",
        "ru": "📝 Начать Тест",
        "en": "📝 Start Test"
    }.get(lang, "📝 Start Test")
    
    status_btn = status_passed if quiz_passed else status_start
    back_lbl = {"uz": "🔙 Orqaga", "uz_cyr": "🔙 Орқага", "ru": "🔙 Назад", "en": "🔙 Back"}.get(lang, "🔙 Orqaga")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status_btn, callback_data="quiz_start_session")],
        [InlineKeyboardButton(text=back_lbl, callback_data="main_menu")]
    ])


def quiz_question_kb(q_idx: int, options: list) -> InlineKeyboardMarkup:
    rows = []
    for option_text, option_val in options:
        rows.append([InlineKeyboardButton(text=option_text, callback_data=f"quiz_ans_{q_idx}_{option_val}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_result_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    btn_text = {
        "uz": "🔙 Bosh Menyuga Qaytish",
        "uz_cyr": "🔙 Бош Менюга Қайтиш",
        "ru": "🔙 Вернуться в главное меню",
        "en": "🔙 Return to main menu"
    }.get(lang, "🔙 Bosh Menyuga Qaytish")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="main_menu")]
    ])


def channel_subscribe_kb(channel_username: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Kanalga obuna bo'lish va tekshirish tugmalari."""
    uname = channel_username.lstrip("@")
    btn_go = {
        "uz": "📢 Kanalga o'tish va obuna bo'lish",
        "uz_cyr": "📢 Каналга ўтиш ва обуна бўлиш",
        "ru": "📢 Перейти в канал и подписаться",
        "en": "📢 Go to channel & subscribe"
    }.get(lang, "📢 Go to channel")
    
    btn_verify = {
        "uz": "✅ Obunani tekshirish",
        "uz_cyr": "✅ Обунани текшириш",
        "ru": "✅ Проверить подписку",
        "en": "✅ Verify subscription"
    }.get(lang, "✅ Verify subscription")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn_go,
            url=f"https://t.me/{uname}",
        )],
        [InlineKeyboardButton(
            text=btn_verify,
            callback_data="check_subscription",
        )],
    ])
