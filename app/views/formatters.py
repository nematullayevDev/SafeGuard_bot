"""Pure-function presenters: domain models / data → telegram text."""
from typing import Sequence

from app.models import (
    BannedSite, BotStats, Group, HistoryEntry, ScanResult, ScanVerdict, User, ForensicCase,
)

_VERDICT_LABEL = {
    ScanVerdict.DANGEROUS: "🔴 XAVFLI",
    ScanVerdict.SUSPICIOUS: "⚠️ SHUBHALI",
    ScanVerdict.SAFE: "✅ XAVFSIZ",
    ScanVerdict.UNKNOWN: "❓ NOMA'LUM",
}
_URL_ADVICE = {
    ScanVerdict.DANGEROUS: "❌ Bu linkni OCHMANG!",
    ScanVerdict.SUSPICIOUS: "⚡ Ehtiyot bo'ing!",
    ScanVerdict.SAFE: "👍 Xavfsiz ko'rinadi.",
    ScanVerdict.UNKNOWN: "⚠️ Natijani o'qishda xatolik.",
}
_FILE_ADVICE = {
    ScanVerdict.DANGEROUS: "❌ Bu faylni O'RNATMANG!",
    ScanVerdict.SUSPICIOUS: "⚡ Ehtiyot bo'ing!",
    ScanVerdict.SAFE: "👍 Xavfsiz ko'rinadi.",
    ScanVerdict.UNKNOWN: "⚠️ Natijani o'qishda xatolik.",
}
_VERDICT_EMOJI = {
    ScanVerdict.SAFE: "✅",
    ScanVerdict.DANGEROUS: "🔴",
    ScanVerdict.SUSPICIOUS: "⚠️",
    ScanVerdict.UNKNOWN: "❓",
}


def mention(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def truncate(s: str, limit: int, suffix: str = "...va boshqalar") -> str:
    return s if len(s) <= limit else s[:limit] + f"\n\n{suffix}"


# ─── Scan results ─────────────────────────────────────
def scan_result(r: ScanResult) -> str:
    if r.error:
        return f"❌ Xatolik: {r.error}"
    icon = "🔗" if r.item_type.value == "link" else "📦"
    label = _VERDICT_LABEL[r.verdict]
    advice_map = _URL_ADVICE if r.item_type.value == "link" else _FILE_ADVICE
    advice = advice_map[r.verdict]
    
    desc_str = f"\nℹ️ <b>Batafsil:</b>\n{r.description}\n" if r.description else ""
    
    return (
        f"{label}\n\n{icon} {r.value}\n{desc_str}\n📊 Tahlil ({r.total_engines} antivirus):\n"
        f"  🔴 Xavfli:      {r.malicious}\n"
        f"  🟡 Shubhali:    {r.suspicious}\n"
        f"  🟢 Xavfsiz:     {r.harmless}\n"
        f"  ⚪ Tekshirmadi: {r.undetected}\n\n{advice}"
    )


def dangerous_file_warning(r: ScanResult, sender_mention: str) -> str:
    emoji = "🔴" if r.verdict is ScanVerdict.DANGEROUS else "⚠️"
    return (
        f"🚨 {emoji} <b>XAVFLI FAYL BLOKLANDI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Yuboruvchi: {sender_mention}\n"
        f"📦 Fayl: <b>{r.value}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{scan_result(r)}\n\n"
        f"⚠️ Guruh azolari bu faylni <b>yuklamang!</b>"
    )


def dangerous_link_warning(r: ScanResult, sender_mention: str) -> str:
    emoji = "🔴" if r.verdict is ScanVerdict.DANGEROUS else "⚠️"
    short = r.value[:50] + "..." if len(r.value) > 50 else r.value
    return (
        f"🚨 {emoji} <b>XAVFLI LINK BLOKLANDI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Yuboruvchi: {sender_mention}\n"
        f"🔗 Link: {short}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{scan_result(r)}\n\n"
        f"⚠️ Guruh a'zolari bu linkni <b>ochmang!</b>"
    )


def blacklisted_link_warning(sender_mention: str) -> str:
    return (
        "🔴 <b>XAVFLI LINK BLOKLANDI!</b>\n"
        f"👤 Yuboruvchi: {sender_mention}\n"
        "📋 Qora ro'yxatda mavjud!"
    )


# ─── Stats / lists ────────────────────────────────────
def stats_text(s: BotStats) -> str:
    return (
        "📊 <b>SafeGuard Bot Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Jami foydalanuvchilar: <b>{s.total_users}</b>\n"
        f"🆕 Bugun qo'shilgan: <b>{s.today_users}</b>\n\n"
        f"🔍 Jami tekshiruvlar: <b>{s.total_scans}</b>\n"
        f"🔴 Xavfli topilgan: <b>{s.dangerous}</b>\n"
        f"⚠️ Shubhali topilgan: <b>{s.suspicious}</b>\n\n"
        f"📋 Qora ro'yxat: <b>{s.bl_count}</b> ta yozuv\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


def users_list(users: Sequence[User]) -> str:
    if not users:
        return "📋 Hali hech kim ro'yxatdan o'tmagan."
    lines = [f"👥 <b>Foydalanuvchilar ro'yxati</b> ({len(users)} ta):\n"]
    for i, u in enumerate(users, 1):
        badge = " 🛡️" if getattr(u, "quiz_passed", 0) else ""
        lines.append(
            f"{i}. {mention(u.user_id, u.display_name)}{badge} | {u.at_username} | "
            f"{u.phone} | {u.registered_at}"
        )
    return truncate("\n".join(lines), 3500)



def history_list(entries: Sequence[HistoryEntry]) -> str:
    if not entries:
        return "📊 Tarixingiz bo'sh.\n\nLink yoki fayl yuboring!"
    lines = []
    for e in entries:
        icon = "🔗" if e.item_type.value == "link" else "📦"
        v = _VERDICT_EMOJI.get(e.verdict, "❓")
        short = e.value[:30] + "..." if len(e.value) > 30 else e.value
        lines.append(f"{v} {icon} {short}\n   🕐 {e.scanned_at}")
    return "📊 Oxirgi tekshiruvlar:\n\n" + "\n\n".join(lines)


def _group_link(g: Group) -> str:
    """Guruh nomiga bosish orqali guruhga o'tadigan link yasaydi."""
    t = g.display_title
    if g.username:
        return f'<a href="https://t.me/{g.username}">{t}</a>'
    # Username yo'q — chat_id orqali link (supergroup va kanallar uchun ishlaydi)
    cid = str(g.chat_id)
    if cid.startswith("-100"):
        cid = cid[4:]
    elif cid.startswith("-"):
        cid = cid[1:]
    # invite_link ham bor bo'lsa uni ishlatamiz
    if getattr(g, "invite_link", ""):
        return f'<a href="{g.invite_link}">{t}</a>'
    return f'<a href="https://t.me/c/{cid}">{t}</a>'


def groups_admin_list(active: Sequence[Group], inactive: Sequence[Group]) -> str:
    total = len(active) + len(inactive)
    lines = [
        "🤖 <b>Bot qo'shilgan guruhlar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Jami: <b>{total}</b> ta guruh\n"
        f"🟢 Aktiv: <b>{len(active)}</b> ta  │  "
        f"🔴 Chiqarilgan: <b>{len(inactive)}</b> ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    if active:
        lines.append("\n🟢 <b>Aktiv guruhlar:</b>\n")
        for i, g in enumerate(active, 1):
            members = f"👥 {g.member_count} a'zo  │  " if getattr(g, "member_count", 0) else ""
            lines.append(
                f"  <b>{i}.</b> ✅ {_group_link(g)}\n"
                f"      {members}📅 {g.added_at or '—'}\n"
            )
    if inactive:
        lines.append("🔴 <b>Chiqarilgan guruhlar:</b>\n")
        for i, g in enumerate(inactive, 1):
            lines.append(
                f"  <b>{i}.</b> ❌ {_group_link(g)}\n"
                f"      🔗 {g.at_username}  │  📅 {g.added_at or '—'}\n"
            )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return truncate("\n".join(lines), 3800, suffix="...")


def groups_user_list(active: Sequence[Group]) -> str:
    lines = [
        "📋 <b>Himoya ostidagi guruhlar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Aktiv guruhlar: <b>{len(active)}</b> ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    for i, g in enumerate(active, 1):
        members = f"👥 {g.member_count} a'zo  │  " if getattr(g, "member_count", 0) else ""
        lines.append(
            f"  <b>{i}.</b> 🛡️ {_group_link(g)}\n"
            f"      {members}📅 {g.added_at or '—'}\n"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return truncate("\n".join(lines), 3800, suffix="...")


def blacklist_view(rows: Sequence[tuple[str, str]], count: int) -> str:
    if not rows:
        return "📋 <b>Qora ro'yxat hozircha bo'sh.</b>"
        
    lines = [
        "📋 <b>SafeGuard — Qora ro'yxat</b>",
        f"🛡️ Hozirda jami: <b>{count}</b> ta xavfli havola aniqlangan.",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    for idx, (val, added) in enumerate(rows, 1):
        short_val = val[:45] + "..." if len(val) > 45 else val
        lines.append(f"<b>{idx}.</b> 🚫 <code>{short_val}</code>")
        lines.append(f"   📅 <i>{added}</i>")
        lines.append("")  # Blank line to separate entries beautifully
        
    if lines[-1] == "":
        lines.pop()
        
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def banned_sites_page(platform_title: str, sites: Sequence[BannedSite],
                      start_num: int, total: int, note: str) -> str:
    end_num = start_num + len(sites) - 1
    body = "\n".join(
        f"🚫 {start_num + idx}. {s.name}{' 🆕' if s.is_new else ''}"
        for idx, s in enumerate(sites)
    )
    text = (
        f"{platform_title} — Taqiqlangan ro'yxat ({total} ta)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Ko'rsatilmoqda: {start_num}-{end_num}\n\n"
        f"{body}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n{note}"
    )
    return text if len(text) <= 4000 else text[:3950] + "\n\n...va boshqalar"


def banned_sites_empty(platform_title: str, note: str) -> str:
    return (
        f"{platform_title} — Taqiqlangan ro'yxat\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📭 Hozircha ro'yxat bo'sh.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{note}"
    )


def nlp_violation_warning(category: str, reason: str, sender_mention: str) -> str:
    cat_label = {
        "extremism": "🧠 DINIY EKSTREMIZM VA RADIKALIZM",
        "drugs": "💊 GIYOHVAND MODDALAR SAVDOSI TARG'IBOTI",
        "bullying": "👤 KIBERBULLING VA HAQORAT TAHDIRI"
    }.get(category, "⚠️ TAXDIDLI MATN")
    
    emoji = {
        "extremism": "🚨🔴",
        "drugs": "🚨💊",
        "bullying": "🚨⚠️"
    }.get(category, "🚨")

    legal_note = {
        "extremism": "⚖️ <b>Huquqiy javobgarlik:</b> O'zR JK 244-1-moddasiga ko'ra jamoat xavfsizligiga tahdid soluvchi materiallarni tarqatish <b>jinoiy javobgarlikka</b> sabab bo'ladi.",
        "drugs": "⚖️ <b>Huquqiy javobgarlik:</b> O'zR JK 273-moddasiga ko'ra giyohvandlik moddalari savdosi va yashirin aylanmasi <b>og'ir jinoiy javobgarlikka</b> sabab bo'ladi.",
        "bullying": "⚖️ <b>Huquqiy javobgarlik:</b> O'zR JK 140-moddasi (Haqorat qilish) hamda MJtK 41-moddasiga muvofiq qonuniy choralar ko'riladi."
    }.get(category, "⚖️ O'zbekiston Respublikasi qonunchiligiga ko'ra javobgarlik mavjud.")
    
    return (
        f"{emoji} <b>XAVFLI MATN ANIQLANDI VA BLOKLANDI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Qonunbuzar:</b> {sender_mention}\n"
        f"📂 <b>Kategoriya:</b> <code>{cat_label}</code>\n"
        f"📝 <b>Tahliliy Izoh:</b> <i>{reason}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{legal_note}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 <i>SafeGuard Kiberxavfsizlik avtomatik nazorat tizimi.</i>"
    )


def nlp_forensic_report(result: dict, raw_text: str) -> str:
    category = result.get("category")
    reason = result.get("reason", "Tahlil yakunlandi.")
    is_viol = result.get("is_violation", False)
    
    status_emoji = "🔴 JINAYAT ALOMATLARI ANIQLANDI" if is_viol else "✅ TIZIM XAVFSIZ"
    status_color = "🚨" if is_viol else "🛡"
    
    cat_label = {
        "extremism": "🧠 Ekstremizm va Radikalizm (O'zR JK 244-1)",
        "drugs": "💊 Giyohvand moddalar aylanmasi (O'zR JK 273)",
        "bullying": "👤 Kiberbulling va Haqorat (O'zR JK 140)"
    }.get(category, "—")
    
    short_text = raw_text[:100] + "..." if len(raw_text) > 100 else raw_text
    
    legal_section = ""
    if is_viol and category:
        legal_section = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚖️ <b>Huquqiy Malakalash:</b>\n"
            f"  {category.upper()} moddasi bo'yicha dalillar arxivi shakllantirildi. Ushbu izlar raqamli ekspertiza va sud-tergov jarayonlarida <b>rasmiy dalil</b> bo'lib xizmat qiladi.\n"
        )

    return (
        f"{status_color} <b>SafeGuard Bot KIBER-TERGOV TIZIMI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Ekspertiza Xulosasi:</b>\n"
        f"  • <b>Holat:</b> <code>{status_emoji}</code>\n"
        f"  • <b>Kategoriya:</b> <b>{cat_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Tekshirilgan Matn:</b>\n"
        f"  <i>\"{short_text}\"</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔬 <b>Tahliliy Izoh:</b>\n"
        f"  <code>{reason}</code>\n"
        f"{legal_section}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 <i>SafeGuard Raqamli Ekspertiza va Kiberxavfsizlik tizimining rasmiy tahlilnomasi.</i>"
    )


def state_sync_result(res: dict) -> str:
    return (
        "🏛 <b>SafeGuard Global Integratsiya Tizimi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Davlat ochiq ma'lumotlar bazalari bilan sinxronizatsiya yakunlandi.\n\n"
        f"📂 <b>Holat:</b> <code>{res['status']}</code>\n"
        f"🚫 <b>Ekstremistik sayt/kanallar:</b> +<b>{res['banned_added']}</b> ta yangi qo'shildi\n"
        f"🔗 <b>Fishing havolalar:</b> +<b>{res['phishing_added']}</b> ta qora ro'yxatga olindi\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📢 <i>Lokal bazalar SafeGuard Kiberxavfsizlik tizimi ro'yxatlari bilan muvaffaqiyatli sinxronlandi.</i>"
    )


def forensic_case_detail(case: ForensicCase) -> str:
    if getattr(case, "chat_username", None):
        group_str = f'<a href="https://t.me/{case.chat_username}">{case.chat_title}</a>'
    else:
        clean_id = str(case.chat_id)
        if clean_id.startswith("-100"):
            clean_id = clean_id[4:]
        elif clean_id.startswith("-"):
            clean_id = clean_id[1:]
        group_str = f'<a href="https://t.me/c/{clean_id}">{case.chat_title}</a>'

    return (
        f"📂 <b>KIBER-TERGOV DALILI (Case ID: #{case.id})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Sana va vaqt: <b>{case.detected_at}</b>\n"
        f"Guruh: {group_str} (ID: {case.chat_id})\n"
        f"Qonunbuzar: 👤 <b>{case.full_name}</b> (@{case.username if case.username else 'yo\'q'}, ID: {case.user_id})\n"
        f"Telefon raqam: <b>{case.phone if case.phone else 'ulashilmagan'}</b>\n\n"
        f"🚨 <b>Kategoriya:</b> <code>{case.display_violation}</code>\n"
        f"🔬 <b>Tizim tahlili:</b> <i>{case.reason}</i>\n\n"
        f"📝 <b>Xabar matni (Dalil):</b>\n"
        f"<i>\"{case.message_text}\"</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"PDF yoki Word bayonnomani yuklab olish uchun quyidagi tugmalardan foydalaning."
    )


def forensics_list_text(category_label: str, total: int, page_num: int, total_pages: int, start_num: int, end_num: int) -> str:
    if total == 0:
        return (
            f"📂 <b>Kiber-Tergov Dalillari Arxivi ({category_label})</b>\n\n"
            f"📭 Hozircha ushbu bo'limda hech qanday tergov dalili mavjud emas.\n\n"
            f"<i>Gumondorlar faoliyati aniqlanganda, tizim avtomatik ravishda bu yerda saqlaydi.</i>"
        )
    return (
        f"📂 <b>Kiber-Tergov Dalillari Arxivi</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Kategoriya: <b>{category_label}</b>\n"
        f"Jami: <b>{total}</b> ta gumondor | Sahifa: <b>{page_num}/{total_pages}</b>\n"
        f"Ko'rsatilmoqda: <b>{start_num}-{end_num}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Batafsil bayonnomani ko'rish uchun quyidagi gumondorlardan birini tanlang:"
    )


def forensic_suspect_detail(suspect_details: dict, cases: Sequence[ForensicCase]) -> str:
    user_id = suspect_details.get("user_id")
    full_name = suspect_details.get("full_name") or "Noma'lum"
    username = suspect_details.get("username") or ""
    phone = suspect_details.get("phone") or "ulashilmagan"
    
    # Clean blank/dot names to avoid empty/dot displays
    if not full_name.strip() or full_name == ".":
        full_name = f"Gumondor #{user_id}"
        
    username_str = f"@{username}" if username else "mavjud emas"
    
    header = (
        f"👤 <b>GUMONDOR PROFILI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Gumondor: <b>{full_name}</b>\n"
        f"Telegram ID: <code>{user_id}</code>\n"
        f"Username: <b>{username_str}</b>\n"
        f"Telefon: <b>{phone}</b>\n"
        f"Jami qonunbuzarliklar soni: <b>{len(cases)} ta</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    body_parts = []
    for idx, case in enumerate(cases, 1):
        if getattr(case, "chat_username", None):
            group_str = f'<a href="https://t.me/{case.chat_username}">{case.chat_title}</a>'
        else:
            clean_id = str(case.chat_id)
            if clean_id.startswith("-100"):
                clean_id = clean_id[4:]
            elif clean_id.startswith("-"):
                clean_id = clean_id[1:]
            group_str = f'<a href="https://t.me/c/{clean_id}">{case.chat_title}</a>'

        body_parts.append(
            f"<b>{idx}-Holat (ID: #{case.id})</b>\n"
            f"📅 Sana: <b>{case.detected_at}</b>\n"
            f"👥 Guruh: {group_str} (ID: {case.chat_id})\n"
            f"🚨 Kategoriya: <code>{case.display_violation}</code>\n"
            f"🔬 Tizim tahlili: <i>{case.reason}</i>\n"
            f"📝 Dalil matni: <i>\"{case.message_text}\"</i>"
        )
    
    # We can join with a nice divider
    body = "\n\n━━━━━━━━━━━━━━━━━━━━━\n\n".join(body_parts)
    
    text = header + body
    if len(text) > 4000:
        text = text[:3950] + "\n\n...va boshqalar (Tarix juda uzun, to'liq ma'lumot PDF/Word faylda)"
    return text


def group_settings_text(chat_title: str, filters: dict) -> str:
    l_status = "🟢 <b>Faol</b> (Fishing havolalar va qora ro'yxat bloklanadi)" if filters.get("filter_links", True) else "🔴 <b>O'chirilgan</b>"
    f_status = "🟢 <b>Faol</b> (Virusli va xavfli fayllar bloklanadi)" if filters.get("filter_files", True) else "🔴 <b>O'chirilgan</b>"
    n_status = "🟢 <b>Faol</b> (Ekstremizm, narkotik va haqoratlar bloklanadi)" if filters.get("filter_nlp", True) else "🔴 <b>O'chirilgan</b>"

    return (
        f"⚙️ <b>«{chat_title}» Guruh Himoyasi Sozlamalari</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Ushbu sahifada botning ushbu guruhdagi himoya modullarini boshqarishingiz mumkin:\n\n"
        f"🔗 <b>Havola Skaneri:</b> {l_status}\n"
        f"📦 <b>Fayl Skaneri:</b> {f_status}\n"
        f"🧠 <b>Matn Tahlili (NLP):</b> {n_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Tegishli modul holatini o'zgartirish uchun quyidagi tugmalarni bosing:</i>"
    )


def quiz_question_text(q_idx: int, question_data: dict) -> str:
    q_num = q_idx + 1
    return (
        f"🛡️ <b>Kiber-Xavfsizlik Viktorinasi</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ <b>Savol {q_num}/5:</b> {question_data['text']}\n\n"
        f"<i>To'g'ri javobni tanlang:</i>"
    )


def quiz_result_text(score: int, passed: bool) -> str:
    status_emoji = "🎉 PASS — TABRIKLAYMIZ!" if passed else "❌ FAILED — Qaytadan urinib ko'ring"
    badge_note = (
        "\n🛡️ Sizga <b>«🛡 Kiber-Himoyalangan»</b> nishoni berildi! "
        "Endi profilingiz va foydalanuvchilar ro'yxatida ushbu belgi aks etadi."
    ) if passed else "\nTestdan o'tish uchun kamida 4 ta savolga to'g'ri javob berishingiz kerak."

    return (
        f"📊 <b>Test Natijalari</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Holat: <b>{status_emoji}</b>\n"
        f"To'g'ri javoblar: <b>{score}/5</b>\n"
        f"Foiz: <b>{score * 20}%</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{badge_note}"
    )





