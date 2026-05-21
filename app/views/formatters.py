"""Pure-function presenters: domain models / data → telegram text."""
from typing import Sequence

from app.models import (
    BannedSite, BotStats, Group, HistoryEntry, ScanResult, ScanVerdict, User,
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
    return (
        f"{label}\n\n{icon} {r.value}\n\n📊 Tahlil ({r.total_engines} antivirus):\n"
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
        lines.append(
            f"{i}. {mention(u.user_id, u.display_name)} | {u.at_username} | "
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


def groups_admin_list(active: Sequence[Group], inactive: Sequence[Group]) -> str:
    lines = [
        "🤖 <b>Bot qo'shilgan barcha guruhlar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Aktiv: <b>{len(active)}</b> ta  |  "
        f"❌ Chiqarilgan: <b>{len(inactive)}</b> ta\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ]
    if active:
        lines.append("\n🟢 <b>Aktiv guruhlar:</b>")
        for i, g in enumerate(active, 1):
            t = g.display_title
            link = f'<a href="https://t.me/{g.username}">{t}</a>' if g.username else f"<b>{t}</b>"
            lines.append(f"{i}. ✅ {link}\n   🔗 {g.at_username}  📅 {g.added_at or '—'}")
    if inactive:
        lines.append("\n🔴 <b>Chiqarilgan guruhlar:</b>")
        for i, g in enumerate(inactive, 1):
            lines.append(
                f"{i}. ❌ <b>{g.display_title}</b>\n"
                f"   🔗 {g.at_username}  📅 {g.added_at or '—'}"
            )
    return truncate("\n".join(lines), 3800, suffix="...")


def groups_user_list(active: Sequence[Group]) -> str:
    lines = [
        "📋 <b>Bot qo'shilgan aktiv guruhlar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Jami: <b>{len(active)}</b> ta\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ]
    for i, g in enumerate(active, 1):
        t = g.display_title
        link = f'<a href="https://t.me/{g.username}">{t}</a>' if g.username else f"<b>{t}</b>"
        lines.append(f"{i}. ✅ {link}\n   🔗 {g.at_username}  📅 {g.added_at or '—'}")
    return truncate("\n".join(lines), 3800, suffix="...")


def blacklist_view(rows: Sequence[tuple[str, str]], count: int) -> str:
    if not rows:
        return "📋 Qora ro'yxat hozircha bo'sh."
    items = "\n".join(
        f"• {v[:50]}{'...' if len(v) > 50 else ''}  ({added})" for v, added in rows
    )
    return f"📋 Qora ro'yxat ({count} ta):\n\n{items}"


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
