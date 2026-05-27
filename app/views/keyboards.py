"""Inline and reply keyboards."""
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
)

from app.core.config import PLATFORMS, settings


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamimni ulashish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def persistent_menu_keyboard(is_admin_user: bool = False) -> ReplyKeyboardMarkup:
    if is_admin_user:
        keyboard = [
            [KeyboardButton(text="📱 Menu"), KeyboardButton(text="👑 Admin")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="📱 Menu")]
        ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def main_menu(is_admin_user: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🚫 Spam Filter", callback_data="spam_filter"),
            InlineKeyboardButton(text="📋 Qora Ro'yxat", callback_data="blacklist"),
        ],
        [
            InlineKeyboardButton(text="📊 Tarixim", callback_data="history"),
            InlineKeyboardButton(text="👥 Guruh Rejimi", callback_data="group_mode"),
        ],
        [InlineKeyboardButton(text="🌐 Taqiqlangan Saytlar", callback_data="banned_sites_main")],
        [
            InlineKeyboardButton(text="🛡️ Kiber-Viktorina", callback_data="quiz_main"),
            InlineKeyboardButton(text="📂 Buyruqlar", callback_data="commands"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help"),
        ],
    ]
    if is_admin_user:
        rows.append([InlineKeyboardButton(text="👑 Admin Paneli", callback_data="admin_panel")])
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
            InlineKeyboardButton(text="🌐 Barchasi", callback_data="admin_forensics_list_p0_call"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ])



def back_button(to: str = "main_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=to)]
    ])


def spam_filter_menu(is_on: bool) -> InlineKeyboardMarkup:
    status = "✅ Yoqiq" if is_on else "❌ O'chiq"
    toggle = "spam_off" if is_on else "spam_on"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Holat: " + status, callback_data=toggle)],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


def blacklist_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Tekshirilgan linklar", callback_data="bl_show")],
        [InlineKeyboardButton(text="🗑 Tozalash (admin)", callback_data="bl_clear")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


def _platform_grid(prefix: str, back_to: str) -> InlineKeyboardMarkup:
    rows = []
    items = list(PLATFORMS.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(text=items[i][1], callback_data=f"{prefix}{items[i][0]}")]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(
                text=items[i + 1][1], callback_data=f"{prefix}{items[i + 1][0]}"
            ))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=back_to)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def banned_sites_menu() -> InlineKeyboardMarkup:
    return _platform_grid("bs_", "main_menu")


def admin_add_site_platforms_menu() -> InlineKeyboardMarkup:
    return _platform_grid("addsite_", "admin_banned_sites")


def group_mode_menu(is_on: bool) -> InlineKeyboardMarkup:
    status = "✅ Yoqiq" if is_on else "❌ O'chiq"
    toggle = "gm_off" if is_on else "gm_on"
    add_url = (
        f"https://t.me/{settings.bot_username}"
        "?startgroup=true&admin=delete_messages+restrict_members+ban_users"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Holat: " + status, callback_data=toggle)],
        [InlineKeyboardButton(text="📋 Guruhlarim", callback_data="gm_list")],
        [InlineKeyboardButton(text="➕ Guruhga qo'shish", url=add_url)],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
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


def go_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Ro'yxatdan o'tish", callback_data="go_start")]
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


def group_settings_kb(chat_id: int, filters: dict) -> InlineKeyboardMarkup:
    l_status = "✅ Faol" if filters.get("filter_links", True) else "❌ O'chirilgan"
    f_status = "✅ Faol" if filters.get("filter_files", True) else "❌ O'chirilgan"
    n_status = "✅ Faol" if filters.get("filter_nlp", True) else "❌ O'chirilgan"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔗 Havolalar (Links)", callback_data="dummy"),
            InlineKeyboardButton(text=l_status, callback_data=f"toggle_gset_{chat_id}_filter_links")
        ],
        [
            InlineKeyboardButton(text="📦 Fayllar (Files/Viruses)", callback_data="dummy"),
            InlineKeyboardButton(text=f_status, callback_data=f"toggle_gset_{chat_id}_filter_files")
        ],
        [
            InlineKeyboardButton(text="🧠 Matn Tahlili (NLP)", callback_data="dummy"),
            InlineKeyboardButton(text=n_status, callback_data=f"toggle_gset_{chat_id}_filter_nlp")
        ],
        [InlineKeyboardButton(text="❌ Yopish", callback_data="close_group_settings")]
    ])


def admin_stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 PDF Hisobot Yuklash", callback_data="admin_stats_pdf")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ])


def quiz_main_menu(quiz_passed: bool) -> InlineKeyboardMarkup:
    status_btn = "🎉 Testdan O'tgansiz (Qayta topshirish)" if quiz_passed else "📝 Testni Boshlash"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status_btn, callback_data="quiz_start_session")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
    ])


def quiz_question_kb(q_idx: int, options: list) -> InlineKeyboardMarkup:
    rows = []
    for option_text, option_val in options:
        rows.append([InlineKeyboardButton(text=option_text, callback_data=f"quiz_ans_{q_idx}_{option_val}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Bosh Menyuga Qaytish", callback_data="main_menu")]
    ])

