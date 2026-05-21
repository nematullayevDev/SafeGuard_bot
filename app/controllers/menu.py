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
    users_export_kb,
)
from app.views.texts import WELCOME

logger = logging.getLogger(__name__)


def register(dp: Dispatcher, c: Container) -> None:

    # ─── Navigation ──────────────────────────
    async def go_start(call: CallbackQuery):
        await call.message.answer("Iltimos /start buyrug'ini yuboring.")
        await call.answer()

    async def home(call: CallbackQuery):
        await call.message.edit_text(
            WELCOME.format(name=call.from_user.first_name or "Foydalanuvchi"),
            reply_markup=main_menu(is_owner(call)),
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
            reply_markup=back_button("admin_panel"), parse_mode="HTML",
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
        user_cmds = (
            "📂 <b>Foydalanuvchi buyruqlari:</b>\n\n"
            "▫️ /start — Botni ishga tushirish\n"
            "▫️ /menu — Bosh menyuni ochish\n"
        )
        admin_cmds = (
            "\n👑 <b>Admin buyruqlari:</b>\n\n"
            "▫️ /users — Foydalanuvchilar ro'yxati\n"
            "▫️ /stats — Bot statistikasi\n"
            "▫️ /broadcast — Xabar tarqatish\n"
        ) if is_owner(call) else ""
        group_cmds = (
            "\n👥 <b>Guruh buyruqlari (admin uchun):</b>\n\n"
            "▫️ /enable — Himoyani yoqish\n"
            "▫️ /disable — Himoyani o'chirish\n"
            "▫️ /status — Himoya holati\n"
            "▫️ /warn — Foydalanuvchiga warn\n"
            "▫️ /warns — Warn sonini ko'rish\n"
            "▫️ /unwarn — Warnlarni tozalash\n"
        )
        await call.message.edit_text(
            user_cmds + admin_cmds + group_cmds,
            reply_markup=back_button(), parse_mode="HTML",
        )
        await call.answer()

    async def help_view(call: CallbackQuery):
        await call.message.edit_text(
            "🆘 Yordam:\n\n"
            "🔗 Link yuboring — tekshiriladi\n"
            "📦 APK/fayl yuboring — tahlil qilinadi\n\n"
            "🚫 Spam Filter — shubhali matnlarni aniqlaydi\n"
            "📋 Qora Ro'yxat — xavfli linklar ro'yxati\n"
            "📊 Tarixim — oxirgi tekshiruvlar\n"
            "👥 Guruh Rejimi — guruhni himoya qilish\n"
            "🌐 Taqiqlangan Saytlar — O'zbekistonda taqiqlangan kontent\n\n"
            f"⚡ <b>Rate limit:</b> {settings.rate_limit_max} ta so'rov / "
            f"{settings.rate_limit_window} sekund",
            reply_markup=back_button(), parse_mode="HTML",
        )
        await call.answer()

    # ─── Spam filter ─────────────────────────
    async def spam_filter_view(call: CallbackQuery):
        is_on = c.user_settings.get_spam_filter(call.from_user.id)
        await call.message.edit_text(
            f"🚫 Spam Filter\n\nHolat: {'✅ Yoqiq' if is_on else '❌ Ochiq'}",
            reply_markup=spam_filter_menu(is_on),
        )
        await call.answer()

    async def spam_on(call: CallbackQuery):
        c.user_settings.set_spam_filter(call.from_user.id, True)
        await call.message.edit_text(
            "🚫 Spam Filter — ✅ Yoqildi!", reply_markup=spam_filter_menu(True)
        )
        await call.answer()

    async def spam_off(call: CallbackQuery):
        c.user_settings.set_spam_filter(call.from_user.id, False)
        await call.message.edit_text(
            "🚫 Spam Filter — ❌ O'chirildi.", reply_markup=spam_filter_menu(False)
        )
        await call.answer()

    # ─── Blacklist ───────────────────────────
    async def blacklist(call: CallbackQuery):
        _, count = c.blacklist.recent()
        await call.message.edit_text(
            f"📋 Qora Ro'yxat\n\nHozirda {count} ta yozuv bor.",
            reply_markup=blacklist_menu(),
        )
        await call.answer()

    async def bl_show(call: CallbackQuery):
        rows, count = c.blacklist.recent()
        await call.message.edit_text(
            formatters.blacklist_view(rows, count),
            reply_markup=blacklist_menu(),
        )
        await call.answer()

    async def bl_clear(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        c.blacklist.clear()
        await call.message.edit_text("🗑 Qora ro'yxat tozalandi!", reply_markup=blacklist_menu())
        await call.answer()

    # ─── History ─────────────────────────────
    async def history_view(call: CallbackQuery):
        entries = c.scanner.history(call.from_user.id)
        await call.message.edit_text(
            formatters.history_list(entries), reply_markup=back_button(),
        )
        await call.answer()

    # ─── Group mode toggle (per-chat) ────────
    async def group_mode_view(call: CallbackQuery):
        chat_id = call.message.chat.id
        is_on = c.user_settings.get_group_mode(chat_id)
        active = len(c.groups.active())
        await call.message.edit_text(
            "👥 Guruh Rejimi\n\n"
            "Xavfli link → xabar o'chiriladi + ogohlantirish + warn\n"
            "3 ta warn → foydalanuvchi ban\n\n"
            f"📌 Qo'shilgan guruhlar: <b>{active}</b> ta\n"
            f"Holat: {'✅ Yoqiq' if is_on else '❌ Ochiq'}",
            reply_markup=group_mode_menu(is_on), parse_mode="HTML",
        )
        await call.answer()

    async def gm_on(call: CallbackQuery):
        c.user_settings.set_group_mode(call.message.chat.id, True)
        active = len(c.groups.active())
        await call.message.edit_text(
            f"👥 Guruh Rejimi — ✅ Yoqildi!\n\n📌 Qo'shilgan guruhlar: <b>{active}</b> ta",
            reply_markup=group_mode_menu(True), parse_mode="HTML",
        )
        await call.answer()

    async def gm_off(call: CallbackQuery):
        c.user_settings.set_group_mode(call.message.chat.id, False)
        active = len(c.groups.active())
        await call.message.edit_text(
            f"👥 Guruh Rejimi — ❌ O'chirildi.\n\n📌 Qo'shilgan guruhlar: <b>{active}</b> ta",
            reply_markup=group_mode_menu(False), parse_mode="HTML",
        )
        await call.answer()

    async def gm_list(call: CallbackQuery):
        active = c.groups.active()
        if not active:
            await call.message.edit_text(
                "📋 <b>Bot qo'shilgan guruhlar</b>\n\n"
                "❗ Hali hech qanday aktiv guruh yo'q.\n\n"
                "➕ <i>Guruhga qo'shish</i> tugmasini bosing!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="group_mode")]
                ]),
                parse_mode="HTML",
            )
        else:
            await call.message.edit_text(
                formatters.groups_user_list(active),
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
