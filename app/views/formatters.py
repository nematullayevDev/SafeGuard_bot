"""Pure-function presenters: domain models / data → telegram text."""
from typing import Sequence

from app.models import (
    BannedSite, BotStats, Group, HistoryEntry, ScanResult, ScanVerdict, User, ForensicCase,
)

_VERDICT_LABEL = {
    "uz": {
        ScanVerdict.DANGEROUS: "🔴 XAVFLI",
        ScanVerdict.SUSPICIOUS: "⚠️ SHUBHALI",
        ScanVerdict.SAFE: "✅ XAVFSIZ",
        ScanVerdict.UNKNOWN: "❓ NOMA'LUM",
    },
    "uz_cyr": {
        ScanVerdict.DANGEROUS: "🔴 ХАВФЛИ",
        ScanVerdict.SUSPICIOUS: "⚠️ ШУБҲАЛИ",
        ScanVerdict.SAFE: "✅ ХАВФСИЗ",
        ScanVerdict.UNKNOWN: "❓ НОМАЪЛУМ",
    },
    "ru": {
        ScanVerdict.DANGEROUS: "🔴 ОПАСНО",
        ScanVerdict.SUSPICIOUS: "⚠️ ПОДОЗРИТЕЛЬНО",
        ScanVerdict.SAFE: "✅ БЕЗОПАСНО",
        ScanVerdict.UNKNOWN: "❓ НЕИЗВЕСТНО",
    },
    "en": {
        ScanVerdict.DANGEROUS: "🔴 DANGEROUS",
        ScanVerdict.SUSPICIOUS: "⚠️ SUSPICIOUS",
        ScanVerdict.SAFE: "✅ SAFE",
        ScanVerdict.UNKNOWN: "❓ UNKNOWN",
    }
}
_URL_ADVICE = {
    "uz": {
        ScanVerdict.DANGEROUS: "❌ Bu linkni OCHMANG!",
        ScanVerdict.SUSPICIOUS: "⚡ Ehtiyot bo'ling!",
        ScanVerdict.SAFE: "👍 Xavfsiz ko'rinadi.",
        ScanVerdict.UNKNOWN: "⚠️ Natijani o'qishda xatolik.",
    },
    "uz_cyr": {
        ScanVerdict.DANGEROUS: "❌ Бу линкни ОЧМАНГ!",
        ScanVerdict.SUSPICIOUS: "⚡ Эҳтиёт бўлинг!",
        ScanVerdict.SAFE: "👍 Хавфсиз кўринади.",
        ScanVerdict.UNKNOWN: "⚠️ Натижани ўқишда хатолик.",
    },
    "ru": {
        ScanVerdict.DANGEROUS: "❌ НЕ ОТКРЫВАЙТЕ эту ссылку!",
        ScanVerdict.SUSPICIOUS: "⚡ Будьте осторожны!",
        ScanVerdict.SAFE: "👍 Выглядит безопасно.",
        ScanVerdict.UNKNOWN: "⚠️ Ошибка при чтении результата.",
    },
    "en": {
        ScanVerdict.DANGEROUS: "❌ DO NOT OPEN this link!",
        ScanVerdict.SUSPICIOUS: "⚡ Be cautious!",
        ScanVerdict.SAFE: "👍 Appears safe.",
        ScanVerdict.UNKNOWN: "⚠️ Error reading result.",
    }
}
_FILE_ADVICE = {
    "uz": {
        ScanVerdict.DANGEROUS: "❌ Bu faylni O'RNATMANG!",
        ScanVerdict.SUSPICIOUS: "⚡ Ehtiyot bo'ling!",
        ScanVerdict.SAFE: "👍 Xavfsiz ko'rinadi.",
        ScanVerdict.UNKNOWN: "⚠️ Natijani o'qishda xatolik.",
    },
    "uz_cyr": {
        ScanVerdict.DANGEROUS: "❌ Бу файлни ЎРНАТМАНГ!",
        ScanVerdict.SUSPICIOUS: "⚡ Эҳтиёт бўлинг!",
        ScanVerdict.SAFE: "👍 Хавфсиз кўринади.",
        ScanVerdict.UNKNOWN: "⚠️ Натижани ўқишда хатолик.",
    },
    "ru": {
        ScanVerdict.DANGEROUS: "❌ НЕ УСТАНАВЛИВАЙТЕ этот файл!",
        ScanVerdict.SUSPICIOUS: "⚡ Будьте осторожны!",
        ScanVerdict.SAFE: "👍 Выглядит безопасно.",
        ScanVerdict.UNKNOWN: "⚠️ Ошибка при чтении результата.",
    },
    "en": {
        ScanVerdict.DANGEROUS: "❌ DO NOT INSTALL this file!",
        ScanVerdict.SUSPICIOUS: "⚡ Be cautious!",
        ScanVerdict.SAFE: "👍 Appears safe.",
        ScanVerdict.UNKNOWN: "⚠️ Error reading result.",
    }
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
def scan_result(r: ScanResult, lang: str = "uz") -> str:
    if r.error:
        if lang == "uz":
            return f"❌ Xatolik: {r.error}"
        elif lang == "uz_cyr":
            return f"❌ Хатолик: {r.error}"
        elif lang == "ru":
            return f"❌ Ошибка: {r.error}"
        else:
            return f"❌ Error: {r.error}"
    icon = "🔗" if r.item_type.value == "link" else "📦"
    
    lang_labels = _VERDICT_LABEL.get(lang, _VERDICT_LABEL["uz"])
    label = lang_labels[r.verdict]
    
    advice_map = _URL_ADVICE if r.item_type.value == "link" else _FILE_ADVICE
    lang_advices = advice_map.get(lang, advice_map["uz"])
    advice = lang_advices[r.verdict]
    
    desc_str = ""
    if r.description:
        desc_label = {
            "uz": "ℹ️ <b>Batafsil:</b>",
            "uz_cyr": "ℹ️ <b>Батафсил:</b>",
            "ru": "ℹ️ <b>Подробнее:</b>",
            "en": "ℹ️ <b>Details:</b>"
        }.get(lang, "ℹ️ <b>Details:</b>")
        desc_str = f"\n{desc_label}\n{r.description}\n"
        
    analysis_label = {
        "uz": f"📊 Tahlil ({r.total_engines} antivirus):",
        "uz_cyr": f"📊 Таҳлил ({r.total_engines} антивирус):",
        "ru": f"📊 Анализ ({r.total_engines} антивирусов):",
        "en": f"📊 Analysis ({r.total_engines} antiviruses):"
    }.get(lang, f"📊 Analysis:")
    
    mal_label = {"uz": "Xavfli", "uz_cyr": "Хавфли", "ru": "Опасно", "en": "Dangerous"}.get(lang, "Dangerous")
    susp_label = {"uz": "Shubhali", "uz_cyr": "Шубҳали", "ru": "Подозрительно", "en": "Suspicious"}.get(lang, "Suspicious")
    safe_label = {"uz": "Xavfsiz", "uz_cyr": "Хавфсиз", "ru": "Безопасно", "en": "Safe"}.get(lang, "Safe")
    un_label = {"uz": "Tekshirmadi", "uz_cyr": "Текширмади", "ru": "Не проверено", "en": "Undetected"}.get(lang, "Undetected")
    
    return (
        f"{label}\n\n{icon} {r.value}\n{desc_str}\n{analysis_label}\n"
        f"  🔴 {mal_label}:      {r.malicious}\n"
        f"  🟡 {susp_label}:    {r.suspicious}\n"
        f"  🟢 {safe_label}:     {r.harmless}\n"
        f"  ⚪ {un_label}: {r.undetected}\n\n{advice}"
    )


def dangerous_file_warning(r: ScanResult, sender_mention: str, lang: str = "uz") -> str:
    emoji = "🔴" if r.verdict is ScanVerdict.DANGEROUS else "⚠️"
    title = {
        "uz": "🚨 {emoji} <b>XAVFLI FAYL BLOKLANDI!</b>",
        "uz_cyr": "🚨 {emoji} <b>ХАВФЛИ ФАЙЛ БЛОКЛАНДИ!</b>",
        "ru": "🚨 {emoji} <b>ВРЕДОНОСНЫЙ ФАЙЛ ЗАБЛОКИРОВАН!</b>",
        "en": "🚨 {emoji} <b>MALICIOUS FILE BLOCKED!</b>"
    }.get(lang, "🚨 {emoji} <b>MALICIOUS FILE BLOCKED!</b>").format(emoji=emoji)
    
    sender_label = {"uz": "Yuboruvchi", "uz_cyr": "Юборувчи", "ru": "Отправитель", "en": "Sender"}.get(lang, "Sender")
    file_label = {"uz": "Fayl", "uz_cyr": "Файл", "ru": "Файл", "en": "File"}.get(lang, "File")
    
    warn_text = {
        "uz": "⚠️ Guruh a'zolari bu faylni <b>yuklamang!</b>",
        "uz_cyr": "⚠️ Гуруҳ аъзолари бу файлни <b>юкламанг!</b>",
        "ru": "⚠️ Участники группы, <b>не скачивайте</b> этот файл!",
        "en": "⚠️ Group members, <b>do not download</b> this file!"
    }.get(lang, "⚠️ Group members, <b>do not download</b> this file!")
    
    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {sender_label}: {sender_mention}\n"
        f"📦 {file_label}: <b>{r.value}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{scan_result(r, lang)}\n\n"
        f"{warn_text}"
    )


def dangerous_link_warning(r: ScanResult, sender_mention: str, lang: str = "uz") -> str:
    emoji = "🔴" if r.verdict is ScanVerdict.DANGEROUS else "⚠️"
    title = {
        "uz": "🚨 {emoji} <b>XAVFLI LINK BLOKLANDI!</b>",
        "uz_cyr": "🚨 {emoji} <b>ХАВФЛИ ЛИНК БЛОКЛАНДИ!</b>",
        "ru": "🚨 {emoji} <b>ВРЕДОНОСНАЯ ССЫЛКА ЗАБЛОКИРОВАНА!</b>",
        "en": "🚨 {emoji} <b>MALICIOUS LINK BLOCKED!</b>"
    }.get(lang, "🚨 {emoji} <b>MALICIOUS LINK BLOCKED!</b>").format(emoji=emoji)
    
    sender_label = {"uz": "Yuboruvchi", "uz_cyr": "Юборувчи", "ru": "Отправитель", "en": "Sender"}.get(lang, "Sender")
    link_label = {"uz": "Link", "uz_cyr": "Линк", "ru": "Ссылка", "en": "Link"}.get(lang, "Link")
    
    warn_text = {
        "uz": "⚠️ Guruh a'zolari bu linkni <b>ochmang!</b>",
        "uz_cyr": "⚠️ Гуруҳ аъзолари бу линкни <b>очманг!</b>",
        "ru": "⚠️ Участники группы, <b>не открывайте</b> эту ссылку!",
        "en": "⚠️ Group members, <b>do not open</b> this link!"
    }.get(lang, "⚠️ Group members, <b>do not open</b> this link!")
    
    short = r.value[:50] + "..." if len(r.value) > 50 else r.value
    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {sender_label}: {sender_mention}\n"
        f"🔗 {link_label}: {short}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{scan_result(r, lang)}\n\n"
        f"{warn_text}"
    )


def blacklisted_link_warning(sender_mention: str, lang: str = "uz") -> str:
    title = {
        "uz": "🔴 <b>XAVFLI LINK BLOKLANDI!</b>",
        "uz_cyr": "🔴 <b>ХАВФЛИ ЛИНК БЛОКЛАНДИ!</b>",
        "ru": "🔴 <b>ВРЕДОНОСНАЯ ССЫЛКА ЗАБЛОКИРОВАНА!</b>",
        "en": "🔴 <b>MALICIOUS LINK BLOCKED!</b>"
    }.get(lang, "🔴 <b>MALICIOUS LINK BLOCKED!</b>")
    
    sender_label = {"uz": "Yuboruvchi", "uz_cyr": "Юборувчи", "ru": "Отправитель", "en": "Sender"}.get(lang, "Sender")
    info = {
        "uz": "📋 Qora ro'yxatda mavjud!",
        "uz_cyr": "📋 Қора рўйхатда мавжуд!",
        "ru": "📋 Находится в черном списке!",
        "en": "📋 Exists in the blacklist!"
    }.get(lang, "📋 Exists in the blacklist!")
    
    return (
        f"{title}\n"
        f"👤 {sender_label}: {sender_mention}\n"
        f"{info}"
    )


# ─── Stats / lists ────────────────────────────────────
def stats_text(s: BotStats, lang: str = "uz") -> str:
    title = {
        "uz": "📊 <b>SafeGuard Bot Statistikasi</b>",
        "uz_cyr": "📊 <b>SafeGuard Бот Статистикаси</b>",
        "ru": "📊 <b>Статистика Бота SafeGuard</b>",
        "en": "📊 <b>SafeGuard Bot Statistics</b>"
    }.get(lang, "📊 <b>SafeGuard Bot Statistics</b>")

    total_lbl = {"uz": "Jami foydalanuvchilar", "uz_cyr": "Жами фойдаланувчилар", "ru": "Всего пользователей", "en": "Total users"}.get(lang, "Total users")
    today_lbl = {"uz": "Bugun qo'shilgan", "uz_cyr": "Бугун қўшилган", "ru": "Добавлено сегодня", "en": "Joined today"}.get(lang, "Joined today")
    scans_lbl = {"uz": "Jami tekshiruvlar", "uz_cyr": "Жами текширувлар", "ru": "Всего проверок", "en": "Total scans"}.get(lang, "Total scans")
    dang_lbl = {"uz": "Xavfli topilgan", "uz_cyr": "Хавфли топилган", "ru": "Найдено опасных", "en": "Flagged dangerous"}.get(lang, "Flagged dangerous")
    susp_lbl = {"uz": "Shubhali topilgan", "uz_cyr": "Шубҳали топилган", "ru": "Найдено подозрительных", "en": "Flagged suspicious"}.get(lang, "Flagged suspicious")
    
    bl_lbl = {
        "uz": f"📋 Qora ro'yxat: <b>{s.bl_count}</b> ta yozuv",
        "uz_cyr": f"📋 Қора рўйхат: <b>{s.bl_count}</b> та ёзув",
        "ru": f"📋 Черный список: <b>{s.bl_count}</b> записей",
        "en": f"📋 Blacklist: <b>{s.bl_count}</b> entries"
    }.get(lang, "")

    return (
        f"{title}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 {total_lbl}: <b>{s.total_users}</b>\n"
        f"🆕 {today_lbl}: <b>{s.today_users}</b>\n\n"
        f"🔍 {scans_lbl}: <b>{s.total_scans}</b>\n"
        f"🔴 {dang_lbl}: <b>{s.dangerous}</b>\n"
        f"⚠️ {susp_lbl}: <b>{s.suspicious}</b>\n\n"
        f"{bl_lbl}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


def users_list(users: Sequence[User], lang: str = "uz") -> str:
    if not users:
        return {
            "uz": "📋 Hali hech kim ro'yxatdan o'tmagan.",
            "uz_cyr": "📋 Ҳали ҳеч ким рўйхатдан ўтмаган.",
            "ru": "📋 Еще никто не зарегистрировался.",
            "en": "📋 No users registered yet."
        }.get(lang, "")
        
    title = {
        "uz": f"👥 <b>Foydalanuvchilar ro'yxati</b> ({len(users)} ta):\n",
        "uz_cyr": f"👥 <b>Фойдаланувчилар рўйхати</b> ({len(users)} та):\n",
        "ru": f"👥 <b>Список пользователей</b> ({len(users)}):\n",
        "en": f"👥 <b>Users list</b> ({len(users)}):\n"
    }.get(lang, "")
    
    lines = [title]
    for i, u in enumerate(users, 1):
        badge = " 🛡️" if getattr(u, "quiz_passed", 0) else ""
        lines.append(
            f"{i}. {mention(u.user_id, u.display_name)}{badge} | {u.at_username} | "
            f"{u.phone} | {u.registered_at}"
        )
    return truncate("\n".join(lines), 3500)


def history_list(entries: Sequence[HistoryEntry], lang: str = "uz") -> str:
    if not entries:
        return {
            "uz": "📊 Tarixingiz bo'sh.\n\nLink yoki fayl yuboring!",
            "uz_cyr": "📊 Тарихингиз бўш.\n\nЛинк ёки файл юборинг!",
            "ru": "📊 Ваша история пуста.\n\nОтправьте ссылку или файл!",
            "en": "📊 Your history is empty.\n\nSend a link or file!"
        }.get(lang, "")
        
    lines = []
    for e in entries:
        icon = "🔗" if e.item_type.value == "link" else "📦"
        v = _VERDICT_EMOJI.get(e.verdict, "❓")
        short = e.value[:30] + "..." if len(e.value) > 30 else e.value
        lines.append(f"{v} {icon} {short}\n   🕐 {e.scanned_at}")
        
    title = {
        "uz": "📊 Oxirgi tekshiruvlar:\n\n",
        "uz_cyr": "📊 Охирги текширувлар:\n\n",
        "ru": "📊 Последние проверки:\n\n",
        "en": "📊 Recent scans:\n\n"
    }.get(lang, "")
    
    return title + "\n\n".join(lines)


def _group_link(g: Group) -> str:
    """Guruh nomiga bosish orqali guruhga o'tadigan link yasaydi."""
    t = g.display_title
    if g.username:
        return f'<a href="https://t.me/{g.username}">{t}</a>'
    cid = str(g.chat_id)
    if cid.startswith("-100"):
        cid = cid[4:]
    elif cid.startswith("-"):
        cid = cid[1:]
    if getattr(g, "invite_link", ""):
        return f'<a href="{g.invite_link}">{t}</a>'
    return f'<a href="https://t.me/c/{cid}">{t}</a>'


def groups_admin_list(active: Sequence[Group], inactive: Sequence[Group], lang: str = "uz") -> str:
    total = len(active) + len(inactive)
    
    title = {
        "uz": "🤖 <b>Bot qo'shilgan guruhlar</b>",
        "uz_cyr": "🤖 <b>Бот қўшилган гуруҳлар</b>",
        "ru": "🤖 <b>Группы, куда добавлен бот</b>",
        "en": "🤖 <b>Groups with bot added</b>"
    }.get(lang, "")
    
    summary = {
        "uz": f"📊 Jami: <b>{total}</b> ta guruh\n🟢 Aktiv: <b>{len(active)}</b> ta  │  🔴 Chiqarilgan: <b>{len(inactive)}</b> ta",
        "uz_cyr": f"📊 Жами: <b>{total}</b> та гуруҳ\n🟢 Актив: <b>{len(active)}</b> та  │  🔴 Чиқарилган: <b>{len(inactive)}</b> та",
        "ru": f"📊 Всего: <b>{total}</b> групп\n🟢 Активных: <b>{len(active)}</b>  │  🔴 Удаленных: <b>{len(inactive)}</b>",
        "en": f"📊 Total: <b>{total}</b> groups\n🟢 Active: <b>{len(active)}</b>  │  🔴 Removed: <b>{len(inactive)}</b>"
    }.get(lang, "")

    lines = [
        title,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        summary,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    lbl_active = {"uz": "Aktiv guruhlar", "uz_cyr": "Актив гуруҳлар", "ru": "Активные группы", "en": "Active groups"}.get(lang, "")
    lbl_inactive = {"uz": "Chiparilgan guruhlar", "uz_cyr": "Чиқарилган гуруҳлар", "ru": "Удаленные группы", "en": "Removed groups"}.get(lang, "")
    lbl_members = {"uz": "a'zo", "uz_cyr": "аъзо", "ru": "участников", "en": "members"}.get(lang, "")
    
    if active:
        lines.append(f"\n🟢 <b>{lbl_active}:</b>\n")
        for i, g in enumerate(active, 1):
            members = f"👥 {g.member_count} {lbl_members}  │  " if getattr(g, "member_count", 0) else ""
            lines.append(
                f"  <b>{i}.</b> ✅ {_group_link(g)}\n"
                f"      {members}📅 {g.added_at or '—'}\n"
            )
    if inactive:
        lines.append(f"🔴 <b>{lbl_inactive}:</b>\n")
        for i, g in enumerate(inactive, 1):
            lines.append(
                f"  <b>{i}.</b> ❌ {_group_link(g)}\n"
                f"      🔗 {g.at_username}  │  📅 {g.added_at or '—'}\n"
            )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return truncate("\n".join(lines), 3800, suffix="...")


def groups_user_list(active: Sequence[Group], lang: str = "uz") -> str:
    title = {
        "uz": "📋 <b>Himoya ostidagi guruhlar</b>",
        "uz_cyr": "📋 <b>Ҳимоя остидаги гуруҳлар</b>",
        "ru": "📋 <b>Группы под защитой</b>",
        "en": "📋 <b>Protected groups</b>"
    }.get(lang, "")
    
    summary = {
        "uz": f"✅ Aktiv guruhlar: <b>{len(active)}</b> ta",
        "uz_cyr": f"✅ Актив гуруҳлар: <b>{len(active)}</b> та",
        "ru": f"✅ Активных групп: <b>{len(active)}</b>",
        "en": f"✅ Active groups: <b>{len(active)}</b>"
    }.get(lang, "")

    lines = [
        title,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        summary,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    lbl_members = {"uz": "a'zo", "uz_cyr": "аъзо", "ru": "участников", "en": "members"}.get(lang, "")
    for i, g in enumerate(active, 1):
        members = f"👥 {g.member_count} {lbl_members}  │  " if getattr(g, "member_count", 0) else ""
        lines.append(
            f"  <b>{i}.</b> 🛡️ {_group_link(g)}\n"
            f"      {members}📅 {g.added_at or '—'}\n"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return truncate("\n".join(lines), 3800, suffix="...")


def blacklist_view(rows: Sequence[tuple[str, str]], count: int, lang: str = "uz") -> str:
    if not rows:
        return {
            "uz": "📋 <b>Qora ro'yxat hozircha bo'sh.</b>",
            "uz_cyr": "📋 <b>Қора рўйхат ҳозирча бўш.</b>",
            "ru": "📋 <b>Черный список пока пуст.</b>",
            "en": "📋 <b>Blacklist is currently empty.</b>"
        }.get(lang, "")
        
    title = {
        "uz": "📋 <b>SafeGuard — Qora ro'yxat</b>",
        "uz_cyr": "📋 <b>SafeGuard — Қора рўйхат</b>",
        "ru": "📋 <b>SafeGuard — Черный список</b>",
        "en": "📋 <b>SafeGuard — Blacklist</b>"
    }.get(lang, "")
    
    summary = {
        "uz": f"🛡️ Hozirda jami: <b>{count}</b> ta xavfli havola aniqlangan.",
        "uz_cyr": f"🛡️ Ҳозирда жами: <b>{count}</b> та хавфли ҳавола аниқланган.",
        "ru": f"🛡️ Всего на данный момент обнаружено: <b>{count}</b> опасных ссылок.",
        "en": f"🛡️ Total dangerous links detected: <b>{count}</b>."
    }.get(lang, "")

    lines = [
        title,
        summary,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    for idx, (val, added) in enumerate(rows, 1):
        short_val = val[:45] + "..." if len(val) > 45 else val
        lines.append(f"<b>{idx}.</b> 🚫 <code>{short_val}</code>")
        lines.append(f"   📅 <i>{added}</i>")
        lines.append("")
        
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


def nlp_violation_warning(category: str, reason: str, sender_mention: str, lang: str = "uz") -> str:
    cat_label = {
        "uz": {
            "extremism": "🧠 Diniy Ekstremizm va Radikalizm (O'zR JK 244-1)",
            "drugs": "💊 Giyohvand moddalar aylanmasi (O'zR JK 273)",
            "bullying": "👤 Kiberbulling va Haqorat (O'zR JK 140)",
            "cybercrime": "💻 Firibgarlik va Kiber-jinoyat (O'zR JK 168)"
        },
        "uz_cyr": {
            "extremism": "🧠 Диний Экстремизм ва Радикализм (ЎзР ЖК 244-1)",
            "drugs": "💊 Гиёҳванд моддалар айланмаси (ЎзР ЖК 273)",
            "bullying": "👤 Кибербуллинг ва Ҳақорат (ЎзР ЖК 140)",
            "cybercrime": "💻 Фирибгарлик ва Кибер-жиноят (ЎзР ЖК 168)"
        },
        "ru": {
            "extremism": "🧠 Религиозный экстремизм и радикализм (УК РУз 244-1)",
            "drugs": "💊 Оборот наркотических средств (УК РУз 273)",
            "bullying": "👤 Кибербуллинг и оскорбления (УК РУз 140)",
            "cybercrime": "💻 Мошенничество и киберпреступность (УК РУз 168)"
        },
        "en": {
            "extremism": "🧠 Religious Extremism & Radicalism (CC RUz 244-1)",
            "drugs": "💊 Drug Trafficking (CC RUz 273)",
            "bullying": "👤 Cyberbullying & Harassment (CC RUz 140)",
            "cybercrime": "💻 Fraud & Cybercrime (CC RUz 168)"
        }
    }.get(lang, {}).get(category, "⚠️ Taqiqlangan matn" if lang == "uz" else "⚠️ Forbidden text")

    legal_note = {
        "uz": {
            "extremism": "O'zR JK 244-1-moddasiga ko'ra jinoiy javobgarlik belgilangan.",
            "drugs": "O'zR JK 273-moddasiga ko'ra og'ir jinoiy javobgarlik belgilangan.",
            "bullying": "O'zR JK 140-moddasiga muvofiq javobgarlik choralari belgilangan.",
            "cybercrime": "O'zR JK 168-moddasiga muvofiq jinoiy javobgarlik belgilangan."
        },
        "uz_cyr": {
            "extremism": "ЎзР ЖК 244-1-моддасига кўра жиноий жавобгарлик белгиланган.",
            "drugs": "ЎзР ЖК 273-моддасига кўра оғир жиноий жавобгарлик белгиланган.",
            "bullying": "ЎзР ЖК 140-моддасига мувофиқ жавобгарлик чоралари белгиланган.",
            "cybercrime": "ЎзР ЖК 168-моддасига мувофиқ жиноий жавобгарлик белгиланган."
        },
        "ru": {
            "extremism": "Уголовная ответственность предусмотрена статьей 244-1 УК РУз.",
            "drugs": "Тяжелая уголовная ответственность предусмотрена статьей 273 УК РУз.",
            "bullying": "Меры ответственности предусмотрены статьей 140 УК РУз.",
            "cybercrime": "Уголовная ответственность предусмотрена статьей 168 УК РУз."
        },
        "en": {
            "extremism": "Criminal liability is established under Article 244-1 of the Criminal Code of RUz.",
            "drugs": "Heavy criminal liability is established under Article 273 of the Criminal Code of RUz.",
            "bullying": "Liability measures are established under Article 140 of the Criminal Code of RUz.",
            "cybercrime": "Criminal liability is established under Article 168 of the Criminal Code of RUz."
        }
    }.get(lang, {}).get(category, "O'zbekiston Respublikasi qonunchiligiga ko'ra javobgarlik belgilangan.")

    title = {
        "uz": "🚨 <b>SafeGuard: Taqiqlangan matn bloklandi!</b>",
        "uz_cyr": "🚨 <b>SafeGuard: Тақиқланган матн блокланди!</b>",
        "ru": "🚨 <b>SafeGuard: Запрещенный текст заблокирован!</b>",
        "en": "🚨 <b>SafeGuard: Forbidden text blocked!</b>"
    }.get(lang, "🚨 <b>SafeGuard: Forbidden text blocked!</b>")

    user_lbl = {"uz": "Foydalanuvchi", "uz_cyr": "Фойдаланувчи", "ru": "Пользователь", "en": "User"}.get(lang, "User")
    cat_lbl = {"uz": "Kategoriya", "uz_cyr": "Категория", "ru": "Категория", "en": "Category"}.get(lang, "Category")
    reason_lbl = {"uz": "Izoh", "uz_cyr": "Изоҳ", "ru": "Пояснение", "en": "Reason"}.get(lang, "Reason")
    action_lbl = {"uz": "Chora", "uz_cyr": "Чора", "ru": "Мера", "en": "Action"}.get(lang, "Action")

    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{user_lbl}:</b> {sender_mention}\n"
        f"📂 <b>{cat_lbl}:</b> <code>{cat_label}</code>\n"
        f"📝 <b>{reason_lbl}:</b> <i>{reason}</i>\n"
        f"⚖️ <b>{action_lbl}:</b> {legal_note}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def nlp_forensic_report(result: dict, raw_text: str, lang: str = "uz") -> str:
    category = result.get("category")
    reason = result.get("reason", "Tahlil yakunlandi.")
    is_viol = result.get("is_violation", False)
    
    title = {
        "uz": "🛡️ <b>Kiber-Tergov Ekspertiza Xulosasi</b>",
        "uz_cyr": "🛡️ <b>Кибер-Тергов Экспертиза Хулосаси</b>",
        "ru": "🛡️ <b>Заключение Кибер-Расследования</b>",
        "en": "🛡️ <b>Cyber-Forensics Investigation Conclusion</b>"
    }.get(lang, "🛡️ <b>Cyber-Forensics Investigation Conclusion</b>")

    if not is_viol:
        safe_msg = {
            "uz": "📊 <b>Holat:</b> ✅ Tizim xavfsiz.\n🔬 <b>Tahlil:</b> Matnda hech qanday kiber-tahdid belgilari aniqlanmadi.",
            "uz_cyr": "📊 <b>Ҳолат:</b> ✅ Тизим хавфсиз.\n🔬 <b>Таҳлил:</b> Матнда ҳеч қандай кибер-таҳдид белгилари аниқланмади.",
            "ru": "📊 <b>Статус:</b> ✅ Система в безопасности.\n🔬 <b>Анализ:</b> В тексте не обнаружено признаков киберугроз.",
            "en": "📊 <b>Status:</b> ✅ System secure.\n🔬 <b>Analysis:</b> No signs of cyber threats detected in the text."
        }.get(lang, "📊 <b>Status:</b> ✅ System secure.\n🔬 <b>Analysis:</b> No signs of cyber threats detected in the text.")
        return (
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{safe_msg}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
    status_emoji = {
        "uz": "🔴 Qonunbuzarlik aniqlandi!",
        "uz_cyr": "🔴 Қонунбузарлик аниқланди!",
        "ru": "🔴 Обнаружено нарушение!",
        "en": "🔴 Violation detected!"
    }.get(lang, "🔴 Violation detected!")
    
    cat_label = {
        "uz": {
            "extremism": "🧠 Ekstremizm va Radikalizm (O'zR JK 244-1)",
            "drugs": "💊 Giyohvand moddalar aylanmasi (O'zR JK 273)",
            "bullying": "👤 Kiberbulling va Haqorat (O'zR JK 140)",
            "cybercrime": "💻 Firibgarlik va Kiberjinoyat (O'zR JK 168)"
        },
        "uz_cyr": {
            "extremism": "🧠 Экстремизм ва Радикализм (ЎзР ЖК 244-1)",
            "drugs": "💊 Гиёҳванд моддалар айланмаси (ЎзР ЖК 273)",
            "bullying": "👤 Кибербуллинг ва Ҳақорат (ЎзР ЖК 140)",
            "cybercrime": "💻 Фирибгарлик ва Кибержиноят (ЎзР ЖК 168)"
        },
        "ru": {
            "extremism": "🧠 Экстремизм и радикализм (УК РУз 244-1)",
            "drugs": "💊 Оборот наркотиков (УК РУз 273)",
            "bullying": "👤 Кибербуллинг и оскорбления (УК РУз 140)",
            "cybercrime": "💻 Мошенничество и киберпреступления (УК РУз 168)"
        },
        "en": {
            "extremism": "🧠 Extremism & Radicalism (CC RUz 244-1)",
            "drugs": "💊 Drug Trafficking (CC RUz 273)",
            "bullying": "👤 Cyberbullying & Harassment (CC RUz 140)",
            "cybercrime": "💻 Fraud & Cybercrime (CC RUz 168)"
        }
    }.get(lang, {}).get(category, "—")
    
    legal_section = {
        "uz": "O'zR JK bo'yicha raqamli dalillar arxivi shakllantirildi.",
        "uz_cyr": "ЎзР ЖК бўйича рақамли далиллар архиви шакллантирилди.",
        "ru": "Сформирован архив цифровых доказательств согласно УК РУз.",
        "en": "Digital evidence archive has been generated according to the Criminal Code of RUz."
    }.get(lang, "Digital evidence archive has been generated.")

    status_lbl = {"uz": "Holat", "uz_cyr": "Ҳолат", "ru": "Статус", "en": "Status"}.get(lang, "Status")
    cat_lbl = {"uz": "Kategoriya", "uz_cyr": "Категория", "ru": "Категория", "en": "Category"}.get(lang, "Category")
    analysis_lbl = {"uz": "Tahlil", "uz_cyr": "Таҳлил", "ru": "Анализ", "en": "Analysis"}.get(lang, "Analysis")
    legal_lbl = {"uz": "Huquqiy chora", "uz_cyr": "Ҳуқуқий чора", "ru": "Правовая мера", "en": "Legal action"}.get(lang, "Legal action")
    evidence_lbl = {
        "uz": "Ushbu izlar sud-tergov jarayonlarida rasmiy dalil bo'lib xizmat qiladi.",
        "uz_cyr": "Ушбу излар суд-тергов жараёнларида расмий далил бўлиб хизмат қилади.",
        "ru": "Данные следы служат официальным доказательством в судебно-следственных процессах.",
        "en": "These traces serve as official evidence in judicial and investigative processes."
    }.get(lang, "These traces serve as official evidence.")

    return (
        f"🚨 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>{status_lbl}:</b> {status_emoji}\n"
        f"📂 <b>{cat_lbl}:</b> <b>{cat_label}</b>\n"
        f"🔬 <b>{analysis_lbl}:</b> <code>{reason}</code>\n"
        f"⚖️ <b>{legal_lbl}:</b> {legal_section} {evidence_lbl}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
    
    return text


def group_settings_text(chat_title: str, filters: dict, g_settings: dict, lang: str = "uz") -> str:
    active_lbl = {"uz": "Faol", "uz_cyr": "Фаол", "ru": "Активен", "en": "Active"}
    inactive_lbl = {"uz": "O'chirilgan", "uz_cyr": "Ўчирилган", "ru": "Отключен", "en": "Disabled"}
    
    l_status = f"🟢 <b>{active_lbl.get(lang, 'Faol')}</b>" if filters.get("filter_links", True) else f"🔴 <b>{inactive_lbl.get(lang, 'O\'chirilgan')}</b>"
    f_status = f"🟢 <b>{active_lbl.get(lang, 'Faol')}</b>" if filters.get("filter_files", True) else f"🔴 <b>{inactive_lbl.get(lang, 'O\'chirilgan')}</b>"
    n_status = f"🟢 <b>{active_lbl.get(lang, 'Faol')}</b>" if filters.get("filter_nlp", True) else f"🔴 <b>{inactive_lbl.get(lang, 'O\'chirilgan')}</b>"

    limit = g_settings.get("warnings_limit", 3)
    kws = g_settings.get("custom_keywords", "")
    wl = g_settings.get("whitelisted_domains", "")
    lang_code = g_settings.get("language", "uz")
    
    lang_names = {
        "uz": "O'zbekcha 🇺🇿",
        "uz_cyr": "Ўзбекча (Крил) 🇺🇿",
        "ru": "Русский 🇷🇺",
        "en": "English 🇬🇧"
    }
    lang_name = lang_names.get(lang_code, "O'zbekcha 🇺🇿")

    no_words = {"uz": "sozlangan so'zlar yo'q", "uz_cyr": "созланган сўзлар йўқ", "ru": "нет настроенных слов", "en": "no keywords configured"}.get(lang, "no keywords configured")
    no_domains = {"uz": "sozlangan domenlar yo'q", "uz_cyr": "созланган доменлар йўқ", "ru": "нет настроенных доменов", "en": "no domains configured"}.get(lang, "no domains configured")

    kws_display = f"<code>{kws}</code>" if kws else f"<i>{no_words}</i>"
    wl_display = f"<code>{wl}</code>" if wl else f"<i>{no_domains}</i>"

    title = {
        "uz": "⚙️ <b>«{chat_title}» Guruh Himoyasi Sozlamalari</b>",
        "uz_cyr": "⚙️ <b>«{chat_title}» Гуруҳ Ҳимояси Созламалари</b>",
        "ru": "⚙️ <b>Настройки Защиты Группы «{chat_title}»</b>",
        "en": "⚙️ <b>«{chat_title}» Group Protection Settings</b>"
    }.get(lang, "⚙️ <b>«{chat_title}» Group Protection Settings</b>").format(chat_title=chat_title)

    link_lbl = {"uz": "Havola Skaneri", "uz_cyr": "Ҳавола Сканери", "ru": "Сканер Ссылок", "en": "Link Scanner"}.get(lang, "Link Scanner")
    file_lbl = {"uz": "Fayl Skaneri", "uz_cyr": "Файл Сканери", "ru": "Сканер Файлов", "en": "File Scanner"}.get(lang, "File Scanner")
    nlp_lbl = {"uz": "Matn Tahlili (NLP)", "uz_cyr": "Матн Таҳлили (NLP)", "ru": "Анализ Текста (NLP)", "en": "Text Analysis (NLP)"}.get(lang, "Text Analysis (NLP)")
    warn_lbl = {"uz": "Ogohlantirishlar Limiti", "uz_cyr": "Огоҳлантиришlar Limiti", "ru": "Лимит Предупреждений", "en": "Warnings Limit"}.get(lang, "Warnings Limit")
    words_lbl = {"uz": "Taqiqlangan so'zlar", "uz_cyr": "Тақиқланган сўзлар", "ru": "Запрещенные слова", "en": "Banned words"}.get(lang, "Banned words")
    wl_lbl = {"uz": "Oq ro'yxat (domenlar)", "uz_cyr": "Оқ рўйхат (доменлар)", "ru": "Белый список (домены)", "en": "Whitelisted domains"}.get(lang, "Whitelisted domains")
    lang_lbl = {"uz": "Guruh tili", "uz_cyr": "Гуруҳ тили", "ru": "Язык группы", "en": "Group language"}.get(lang, "Group language")
    hint = {
        "uz": "👇 <i>Tegishli sozlamani o'zgartirish uchun quyidagi tugmalarni bosing:</i>",
        "uz_cyr": "👇 <i>Тегишли созламани ўзгартириш учун қуйидаги тугмаларни босинг:</i>",
        "ru": "👇 <i>Нажмите кнопки ниже, чтобы изменить настройки:</i>",
        "en": "👇 <i>Press the buttons below to change respective settings:</i>"
    }.get(lang, "👇 <i>Press the buttons below to change respective settings:</i>")

    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>{link_lbl}:</b> {l_status}\n"
        f"📦 <b>{file_lbl}:</b> {f_status}\n"
        f"🧠 <b>{nlp_lbl}:</b> {n_status}\n\n"
        f"⚠️ <b>{warn_lbl}:</b> <code>{limit}</code> ta warn\n"
        f"🚫 <b>{words_lbl}:</b> {kws_display}\n"
        f"✅ <b>{wl_lbl}:</b> {wl_display}\n"
        f"🌐 <b>{lang_lbl}:</b> <code>{lang_name}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{hint}"
    )


def quiz_question_text(q_idx: int, question_data: dict, lang: str = "uz") -> str:
    q_num = q_idx + 1
    title = {
        "uz": "🛡️ <b>Kiber-Xavfsizlik Viktorinasi</b>",
        "uz_cyr": "🛡️ <b>Кибер-Хавфсизлик Викторинаси</b>",
        "ru": "🛡️ <b>Викторина по Кибербезопасности</b>",
        "en": "🛡️ <b>Cyber-Security Quiz</b>"
    }.get(lang, "🛡️ <b>Cyber-Security Quiz</b>")
    
    q_lbl = {"uz": "Savol", "uz_cyr": "Савол", "ru": "Вопрос", "en": "Question"}.get(lang, "Question")
    hint = {
        "uz": "<i>To'g'ri javobni tanlang:</i>",
        "uz_cyr": "<i>Тўғри жавобни танланг:</i>",
        "ru": "<i>Выберите правильный ответ:</i>",
        "en": "<i>Choose the correct answer:</i>"
    }.get(lang, "<i>Choose the correct answer:</i>")

    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ <b>{q_lbl} {q_num}/5:</b> {question_data['text']}\n\n"
        f"{hint}"
    )


def quiz_result_text(score: int, passed: bool, lang: str = "uz") -> str:
    status_emoji = ""
    if passed:
        status_emoji = {
            "uz": "🎉 PASS — TABRIKLAYMIZ!",
            "uz_cyr": "🎉 PASS — ТАБРИКЛАЙМИЗ!",
            "ru": "🎉 СДАНО — ПОЗДРАВЛЯЕМ!",
            "en": "🎉 PASSED — CONGRATULATIONS!"
        }.get(lang, "🎉 PASSED — CONGRATULATIONS!")
    else:
        status_emoji = {
            "uz": "❌ FAILED — Qaytadan urinib ko'ring",
            "uz_cyr": "❌ FAILED — Қайтадан уриниб кўринг",
            "ru": "❌ НЕ СДАНO — Попробуйте снова",
            "en": "❌ FAILED — Try again"
        }.get(lang, "❌ FAILED — Try again")

    badge_note = ""
    if passed:
        badge_note = {
            "uz": "\n🛡️ Sizga <b>«🛡 Kiber-Himoyalangan»</b> nishoni berildi! Endi profilingiz va foydalanuvchilar ro'yxatida ushbu belgi aks etadi.",
            "uz_cyr": "\n🛡️ Сизга <b>«🛡  Кибер-Ҳимояланган»</b> нишони берилди! Энди профилингиз ва фойдаланувчилар рўйхатида ушбу белги акс этади.",
            "ru": "\n🛡️ Вам присвоен знак <b>«🛡 Кибер-защищен»</b>! Теперь этот значок будет отображаться в вашем профиле и списке пользователей.",
            "en": "\n🛡️ You have been awarded the <b>«🛡 Cyber-Protected»</b> badge! This badge will now be displayed on your profile and in the users list."
        }.get(lang, "")
    else:
        badge_note = {
            "uz": "\nTestdan o'tish uchun kamida 4 ta savolga to'g'ri javob berishingiz kerak.",
            "uz_cyr": "\nТестдан ўтиш учун камида 4 та саволга тўғри жавоб беришингиз керак.",
            "ru": "\nДля прохождения теста необходимо правильно ответить минимум на 4 вопроса.",
            "en": "\nYou need to answer at least 4 questions correctly to pass the test."
        }.get(lang, "")

    title = {
        "uz": "📊 <b>Test Natijalari</b>",
        "uz_cyr": "📊 <b>Тест Натижалари</b>",
        "ru": "📊 <b>Результаты Теста</b>",
        "en": "📊 <b>Test Results</b>"
    }.get(lang, "📊 <b>Test Results</b>")

    status_lbl = {"uz": "Holat", "uz_cyr": "Ҳолат", "ru": "Статус", "en": "Status"}.get(lang, "Status")
    correct_lbl = {"uz": "To'g'ri javoblar", "uz_cyr": "Тўғри жавоблар", "ru": "Правильные ответы", "en": "Correct answers"}.get(lang, "Correct answers")
    percent_lbl = {"uz": "Foiz", "uz_cyr": "Foiz", "ru": "Процент", "en": "Percentage"}.get(lang, "Percentage")

    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_lbl}: <b>{status_emoji}</b>\n"
        f"{correct_lbl}: <b>{score}/5</b>\n"
        f"{percent_lbl}: <b>{score * 20}%</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{badge_note}"
    )








