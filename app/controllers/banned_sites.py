"""Banned-sites callbacks (browse, paginate, export, delete, admin add)."""
import logging
import os
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, FSInputFile, InlineKeyboardButton,
    InlineKeyboardMarkup, Message,
)

from app.container import Container
from app.controllers.filters import deny_if_not_owner, is_owner
from app.core.bot import bot
from app.core.config import PLATFORM_NOTES, PLATFORMS, settings
from app.states import AddSiteState
from app.views import formatters
from app.views.keyboards import (
    admin_add_site_platforms_menu, after_addsite_kb, back_button,
    banned_detail_kb, banned_empty_kb, banned_sites_menu, main_menu,
)

logger = logging.getLogger(__name__)

FIRST_PAGE_SIZE = 2
OTHER_PAGE_SIZE = 20
DEL_PAGE_SIZE = 40


def _parse_platform_page(raw: str) -> tuple[str, int]:
    if "_p" in raw:
        platform, _, page_str = raw.rpartition("_p")
        try:
            return platform, int(page_str)
        except ValueError:
            return raw, 0
    return raw, 0


def register(dp: Dispatcher, c: Container) -> None:

    async def banned_main(call: CallbackQuery):
        await call.message.edit_text(
            "🌐 <b>O'zbekistonda taqiqlangan ijtimoiy tarmoq kontentlari</b>\n\n"
            "Quyidagi ijtimoiy tarmoqni tanlang:\n\n"
            "📌 Ma'lumotlar O'zR qonunchiligi asosida tuzilgan",
            reply_markup=banned_sites_menu(), parse_mode="HTML",
        )
        await call.answer()

    async def banned_detail(call: CallbackQuery):
        raw = call.data[len("bs_"):]
        platform, page = _parse_platform_page(raw)
        if platform not in PLATFORMS:
            await call.answer("Ma'lumot topilmadi", show_alert=True)
            return

        title = PLATFORMS[platform]
        note = PLATFORM_NOTES.get(platform, "")
        sites = c.banned_sites.for_platform(platform)

        if not sites:
            await call.message.edit_text(
                formatters.banned_sites_empty(title, note),
                reply_markup=banned_empty_kb(platform), parse_mode="HTML",
            )
            await call.answer()
            return

        if page == 0:
            window = sites[:FIRST_PAGE_SIZE]
            start_num = 1
            has_next = len(sites) > FIRST_PAGE_SIZE
            has_prev = False
        else:
            offset = FIRST_PAGE_SIZE + (page - 1) * OTHER_PAGE_SIZE
            window = sites[offset:offset + OTHER_PAGE_SIZE]
            start_num = offset + 1
            has_next = (offset + OTHER_PAGE_SIZE) < len(sites)
            has_prev = True

        await call.message.edit_text(
            formatters.banned_sites_page(title, window, start_num, len(sites), note),
            reply_markup=banned_detail_kb(
                platform, has_prev=has_prev, has_next=has_next,
                page=page, is_admin_user=is_owner(call),
            ),
            parse_mode="HTML",
        )
        await call.answer()

    def _build_delete_kb(platform: str, page: int, sites) -> tuple[InlineKeyboardMarkup, int, int, int]:
        total_pages = max(1, (len(sites) + DEL_PAGE_SIZE - 1) // DEL_PAGE_SIZE)
        page = max(0, min(page, total_pages - 1))
        window = sites[page * DEL_PAGE_SIZE:(page + 1) * DEL_PAGE_SIZE]

        rows = []
        for i in range(0, len(window), 2):
            row_btns = []
            for j in range(2):
                if i + j < len(window):
                    s = window[i + j]
                    short = s.name[:18] + ".." if len(s.name) > 18 else s.name
                    mark = "🆕" if s.is_new else ""
                    row_btns.append(InlineKeyboardButton(
                        text=f"🗑 {s.id}. {short} {mark}".strip(),
                        callback_data=f"bsdel_{s.id}_{platform}_p{page}",
                    ))
            rows.append(row_btns)

        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(
                text="◀️ Oldingi", callback_data=f"bsdel_list_{platform}_p{page - 1}"
            ))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(
                text="Keyingi ▶️", callback_data=f"bsdel_list_{platform}_p{page + 1}"
            ))
        if nav:
            rows.append(nav)
        rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"bs_{platform}")])

        start = page * DEL_PAGE_SIZE + 1
        end = min((page + 1) * DEL_PAGE_SIZE, len(sites))
        return InlineKeyboardMarkup(inline_keyboard=rows), start, end, total_pages

    async def banned_delete_list(call: CallbackQuery, state: FSMContext):
        if await deny_if_not_owner(call):
            return
        raw = call.data.replace("bsdel_list_", "")
        platform, page = _parse_platform_page(raw)
        sites = c.banned_sites.for_platform(platform)
        if not sites:
            await call.answer("Ro'yxat bo'sh!", show_alert=True)
            return
        kb, start_num, end_num, total_pages = _build_delete_kb(platform, page, sites)
        page = max(0, min(page, total_pages - 1))
        await call.message.edit_text(
            f"🗑 <b>O'chirish uchun saytni tanlang</b>\n\n"
            f"Platform: {PLATFORMS.get(platform, platform)}\n"
            f"Ko'rsatilmoqda: {start_num}-{end_num} / Jami {len(sites)} ta\n"
            f"(Sahifa {page + 1}/{total_pages})",
            reply_markup=kb, parse_mode="HTML",
        )
        await call.answer()

    async def banned_delete_confirm(call: CallbackQuery):
        if await deny_if_not_owner(call):
            return
        raw = call.data[len("bsdel_"):]
        parts = raw.split("_", 1)
        try:
            site_id = int(parts[0])
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return
        rest = parts[1] if len(parts) > 1 else ""
        platform, page = _parse_platform_page(rest)

        site = c.banned_sites.get(site_id)
        if not site:
            await call.answer("Topilmadi!", show_alert=True)
            return

        c.banned_sites.delete(site_id)
        await call.answer(f"✅ '{site.name}' o'chirildi!", show_alert=True)

        sites = c.banned_sites.for_platform(platform)
        if not sites:
            await call.message.edit_text(
                f"✅ {PLATFORMS.get(platform, platform)} ro'yxati bo'shatildi.",
                reply_markup=back_button(f"bs_{platform}"),
            )
            return

        kb, start_num, end_num, _ = _build_delete_kb(platform, page, sites)
        await call.message.edit_text(
            f"🗑 <b>O'chirish uchun saytni tanlang</b>\n\n"
            f"Platform: {PLATFORMS.get(platform, platform)}\n"
            f"Ko'rsatilmoqda: {start_num}-{end_num} / Jami {len(sites)} ta",
            reply_markup=kb, parse_mode="HTML",
        )

    async def banned_export(call: CallbackQuery):
        parts = call.data.split("_", 2)
        if len(parts) < 3:
            await call.answer("Xatolik!", show_alert=True)
            return
        fmt = parts[1]
        platform = parts[2]
        title = PLATFORMS.get(platform, platform)
        sites = c.banned_sites.for_platform(platform)
        if not sites:
            await call.answer("Ro'yxat bo'sh!", show_alert=True)
            return

        items = [f"🚫 {s.id}. {s.name}" for s in sites]
        note = PLATFORM_NOTES.get(platform, "")
        wait = await call.message.answer("⏳ Fayl tayyorlanmoqda...")
        try:
            if fmt == "pdf":
                path = c.exporter.banned_pdf(f"{title} — Taqiqlangan ro'yxat", items, note)
                fname = f"banned_{platform}_{datetime.now():%d%m%Y}.pdf"
            else:
                path = c.exporter.banned_docx(f"{title} — Taqiqlangan ro'yxat", items, note)
                fname = f"banned_{platform}_{datetime.now():%d%m%Y}.docx"
            await bot.send_document(
                call.from_user.id, FSInputFile(path, filename=fname), caption=f"🚫 {title}"
            )
            os.unlink(path)
        except Exception as e:
            logger.error("Banned export xato: %s", e)
            await call.message.answer(f"❌ Xatolik: {e}")
        await wait.delete()
        await call.answer()

    async def admin_add_site(call: CallbackQuery, state: FSMContext):
        if await deny_if_not_owner(call):
            return
        await call.message.edit_text(
            "➕ <b>Yangi sayt qo'shish</b>\n\n"
            "Qaysi ijtimoiy tarmoqqa qo'shmoqchisiz?",
            reply_markup=admin_add_site_platforms_menu(), parse_mode="HTML",
        )
        await state.set_state(AddSiteState.choosing_platform)
        await call.answer()

    async def addsite_platform_chosen(call: CallbackQuery, state: FSMContext):
        if await deny_if_not_owner(call):
            return
        platform = call.data.replace("addsite_", "")
        if platform not in PLATFORMS:
            await call.answer("Noto'g'ri platform!", show_alert=True)
            return
        await state.update_data(platform=platform)
        await state.set_state(AddSiteState.waiting_site_name)
        await call.message.edit_text(
            f"➕ <b>{PLATFORMS[platform]}</b> — Yangi sayt qo'shish\n\n"
            "📝 Sayt/kanal/sahifa nomini yuboring:\n\n"
            "<i>Bekor qilish uchun /cancel yuboring</i>",
            reply_markup=None, parse_mode="HTML",
        )
        await call.answer()

    async def addsite_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu(is_owner(message)))

    async def addsite_name(message: Message, state: FSMContext):
        if message.from_user.id != settings.admin_id:
            await state.clear()
            return
        data = await state.get_data()
        platform = data.get("platform", "telegram")
        name = (message.text or "").strip()
        if len(name) < 2:
            await message.answer("⚠️ Nom juda qisqa! Qayta kiriting:")
            return

        new_id = c.banned_sites.add(platform, name)
        total = c.banned_sites.count(platform)
        await state.clear()
        title = PLATFORMS.get(platform, platform)
        await message.answer(
            f"✅ <b>Qo'shildi!</b>\n\n"
            f"Platform: {title}\n"
            f"🚫 #{new_id}. {name} 🆕\n\n"
            f"Jami {title}: <b>{total}</b> ta\n\n"
            f"Yana qo'shish uchun Admin Panelga o'ting.",
            parse_mode="HTML", reply_markup=after_addsite_kb(),
        )

    dp.callback_query.register(banned_main, F.data == "banned_sites_main")
    dp.callback_query.register(
        banned_detail,
        F.data.startswith("bs_") & ~F.data.startswith("bsdel_") & ~F.data.startswith("bsexp_"),
    )
    dp.callback_query.register(banned_delete_list, F.data.startswith("bsdel_list_"))
    dp.callback_query.register(
        banned_delete_confirm,
        F.data.startswith("bsdel_") & ~F.data.startswith("bsdel_list_"),
    )
    dp.callback_query.register(banned_export, F.data.startswith("bsexp_"))
    dp.callback_query.register(admin_add_site, F.data == "admin_add_site")
    dp.callback_query.register(
        addsite_platform_chosen,
        F.data.startswith("addsite_"), AddSiteState.choosing_platform,
    )
    dp.message.register(addsite_cancel, AddSiteState.waiting_site_name, Command("cancel"))
    dp.message.register(addsite_name, AddSiteState.waiting_site_name)
