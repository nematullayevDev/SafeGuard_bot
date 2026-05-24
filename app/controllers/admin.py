"""Admin commands (/users, /stats, /broadcast) and export callbacks."""
import logging
import os
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.container import Container
from app.controllers.filters import IsAdmin
from app.core.bot import bot
from app.core.config import settings
from app.states import BroadcastState
from app.views import formatters
from app.views.keyboards import users_export_kb, forensics_list_kb, forensic_detail_kb, back_button
from app.views.texts import ADMIN_ONLY, ADMIN_ONLY_ALERT

logger = logging.getLogger(__name__)


def register(dp: Dispatcher, c: Container) -> None:
    is_admin = IsAdmin()

    async def cmd_users(message: Message):
        users = c.users.all()
        if not users:
            await message.answer("📋 Hali hech kim ro'yxatdan o'tmagan.")
            return
        await message.answer(
            formatters.users_list(users),
            parse_mode="HTML", reply_markup=users_export_kb(),
        )

    async def cmd_users_denied(message: Message):
        await message.answer(ADMIN_ONLY)

    async def cmd_stats(message: Message):
        await message.answer(formatters.stats_text(c.stats.get()), parse_mode="HTML")

    async def cmd_broadcast(message: Message, state: FSMContext):
        await message.answer(
            "📢 <b>Broadcast xabari</b>\n\n"
            "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting.\n"
            "Bekor qilish uchun /cancel yuboring.",
            parse_mode="HTML",
        )
        await state.set_state(BroadcastState.waiting_message)

    async def broadcast_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("❌ Broadcast bekor qilindi.")

    async def broadcast_send(message: Message, state: FSMContext):
        await state.clear()
        text = f"📢 <b>SafeGuard Bot xabari:</b>\n\n{message.text or ''}"
        status = await message.answer("⏳ Yuborilmoqda... (0/?)")

        async def on_progress(done: int, total: int) -> None:
            try:
                await status.edit_text(f"⏳ Yuborilmoqda... ({done}/{total})")
            except Exception:
                pass

        sent, failed = await c.broadcaster.send(text, on_progress=on_progress)
        await status.edit_text(
            f"✅ Broadcast yakunlandi!\n\n📨 Yuborildi: {sent}\n❌ Xatolik: {failed}"
        )

    async def handle_users_export(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        wait = await call.message.answer("⏳ Fayl tayyorlanmoqda...")
        users = c.users.all()
        try:
            if call.data == "export_pdf":
                path = c.exporter.users_pdf(users)
                fname = f"users_{datetime.now():%d%m%Y}.pdf"
                caption = "📄 Foydalanuvchilar ro'yxati (PDF)"
            else:
                path = c.exporter.users_docx(users)
                fname = f"users_{datetime.now():%d%m%Y}.docx"
                caption = "📝 Foydalanuvchilar ro'yxati (DOCX)"
            await bot.send_document(
                call.from_user.id, FSInputFile(path, filename=fname), caption=caption,
            )
            os.unlink(path)
        except Exception as e:
            logger.error("Users export xato: %s", e)
            await call.message.answer(f"❌ Xatolik: {e}")
        await wait.delete()
        await call.answer()

    async def handle_groups_export(call: CallbackQuery):
        all_groups = c.groups.all()
        if call.from_user.id == settings.admin_id:
            groups = all_groups
        else:
            groups = [g for g in all_groups if g.is_active]
        wait = await call.message.answer("⏳ Fayl tayyorlanmoqda...")
        try:
            if call.data == "groups_export_pdf":
                path = c.exporter.groups_pdf(groups)
                fname = f"groups_{datetime.now():%d%m%Y}.pdf"
                caption = "📋 Guruhlar ro'yxati (PDF)"
            else:
                path = c.exporter.groups_docx(groups)
                fname = f"groups_{datetime.now():%d%m%Y}.docx"
                caption = "📋 Guruhlar ro'yxati (DOCX)"
            await bot.send_document(
                call.from_user.id, FSInputFile(path, filename=fname), caption=caption,
            )
            os.unlink(path)
        except Exception as e:
            logger.error("Groups export xato: %s", e)
            await call.message.answer(f"❌ Xatolik: {e}")
        await wait.delete()
        await call.answer()

    # ─── State Sync ───────────────────────────────────
    FORENSICS_PAGE_SIZE = 20

    async def admin_state_sync(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        wait = await call.message.answer("🏛 Davlat bazalari bilan sinxronizatsiya boshlanmoqda...")
        try:
            res = await c.state_sync.sync_databases()
            try:
                await wait.delete()
            except Exception:
                pass
            await call.message.edit_text(
                formatters.state_sync_result(res),
                parse_mode="HTML",
                reply_markup=back_button("admin_panel"),
            )
        except Exception as e:
            logger.error("State sync xato: %s", e)
            try:
                await wait.delete()
            except Exception:
                pass
            await call.message.answer(f"❌ Sinxronizatsiya xatosi: {e}")
        await call.answer()

    # ─── Forensics ────────────────────────────────────
    async def admin_forensics_list(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        
        # admin_forensics_list_p{page}_c{category}
        raw = call.data.replace("admin_forensics_list_p", "")
        parts = raw.split("_c")
        page = 0
        category = "all"
        try:
            page = int(parts[0])
            if len(parts) > 1:
                category = parts[1]
        except ValueError:
            pass

        if category == "all":
            all_cases = c.forensics.list_all(limit=1000)
        else:
            all_cases = c.forensics.list_filtered(category, limit=1000)
            
        total = len(all_cases)
        
        start = page * FORENSICS_PAGE_SIZE
        end = start + FORENSICS_PAGE_SIZE
        window = all_cases[start:end]
        has_prev = page > 0
        has_next = end < total

        category_label = {
            "extremism": "🚨 Ekstremizm",
            "drugs": "💊 Giyohvandlik",
            "bullying": "⚠️ Kiberbulling",
            "all": "🌐 Barcha dalillar",
        }.get(category, "Tergov")

        if not all_cases:
            await call.message.edit_text(
                f"📂 <b>Kiber-Tergov Dalillari Arxivi ({category_label})</b>\n\n"
                f"📭 Hozircha ushbu bo'limda hech qanday tergov dalili mavjud emas.\n\n"
                f"<i>Gumondorlar faoliyati aniqlanganda, tizim avtomatik ravishda bu yerda saqlaydi.</i>",
                parse_mode="HTML",
                reply_markup=forensics_list_kb([], 0, False, False, category),
            )
            await call.answer()
            return

        await call.message.edit_text(
            f"📂 <b>Kiber-Tergov Dalillari Arxivi</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Kategoriya: <b>{category_label}</b>\n"
            f"Jami: <b>{total}</b> ta dalil | "
            f"Sahifa: {page + 1}/{max(1, (total + FORENSICS_PAGE_SIZE - 1) // FORENSICS_PAGE_SIZE)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Batafsil ko'rish uchun dalilni tanlang:",
            parse_mode="HTML",
            reply_markup=forensics_list_kb(window, page, has_prev, has_next, category),
        )
        await call.answer()

    async def forensic_case_view(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        # forensic_case_{id}_p{page}_c{category}
        raw = call.data.replace("forensic_case_", "")
        parts = raw.split("_p")
        try:
            case_id = int(parts[0])
            subparts = parts[1].split("_c")
            page = int(subparts[0])
            category = subparts[1] if len(subparts) > 1 else "all"
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        case = c.forensics.get(case_id)
        if not case:
            await call.answer("Dalil topilmadi!", show_alert=True)
            return

        await call.message.edit_text(
            formatters.forensic_case_detail(case),
            parse_mode="HTML",
            reply_markup=forensic_detail_kb(case_id, page, category),
        )
        await call.answer()

    async def forensic_export(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        # forensic_pdf_{id} or forensic_docx_{id}
        parts = call.data.split("_")
        fmt = parts[1]  # pdf or docx
        try:
            case_id = int(parts[2])
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        case = c.forensics.get(case_id)
        if not case:
            await call.answer("Dalil topilmadi!", show_alert=True)
            return

        wait = await call.message.answer("⏳ Tergov bayonnomasi tayyorlanmoqda...")
        try:
            if fmt == "pdf":
                path = c.exporter.forensic_report_pdf(case)
                fname = f"forensic_report_{case_id}_{datetime.now():%d%m%Y}.pdf"
                caption = f"📄 Tergov Bayonnomasi #{case_id} (PDF)"
            else:
                path = c.exporter.forensic_report_docx(case)
                fname = f"forensic_report_{case_id}_{datetime.now():%d%m%Y}.docx"
                caption = f"📝 Tergov Bayonnomasi #{case_id} (DOCX)"
            await bot.send_document(
                call.from_user.id, FSInputFile(path, filename=fname), caption=caption,
            )
            os.unlink(path)
        except Exception as e:
            logger.error("Forensic export xato: %s", e)
            await call.message.answer(f"❌ Xatolik: {e}")
        try:
            await wait.delete()
        except Exception:
            pass
        await call.answer()

    async def forensic_delete(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        # forensic_del_{id}_p{page}_c{category}
        raw = call.data.replace("forensic_del_", "")
        parts = raw.split("_p")
        try:
            case_id = int(parts[0])
            subparts = parts[1].split("_c")
            page = int(subparts[0])
            category = subparts[1] if len(subparts) > 1 else "all"
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        case = c.forensics.get(case_id)
        if not case:
            await call.answer("Dalil topilmadi!", show_alert=True)
            return

        # Profil rasmini ham o'chirish
        if case.photo_path and os.path.exists(case.photo_path):
            try:
                os.unlink(case.photo_path)
            except Exception:
                pass

        c.forensics.delete(case_id)
        await call.answer(f"✅ Dalil #{case_id} o'chirildi!", show_alert=True)

        # Ro'yxatga qaytish
        if category == "all":
            all_cases = c.forensics.list_all(limit=1000)
        else:
            all_cases = c.forensics.list_filtered(category, limit=1000)
            
        total = len(all_cases)
        start = page * FORENSICS_PAGE_SIZE
        end = start + FORENSICS_PAGE_SIZE
        window = all_cases[start:end]
        has_prev = page > 0
        has_next = end < total

        category_label = {
            "extremism": "🚨 Ekstremizm",
            "drugs": "💊 Giyohvandlik",
            "bullying": "⚠️ Kiberbulling",
            "all": "🌐 Barcha dalillar",
        }.get(category, "Tergov")

        if not all_cases:
            await call.message.edit_text(
                f"📂 <b>Kiber-Tergov Dalillari Arxivi ({category_label})</b>\n\n📭 Arxiv bo'sh.",
                parse_mode="HTML",
                reply_markup=back_button("admin_panel"),
            )
            return

        await call.message.edit_text(
            f"📂 <b>Kiber-Tergov Dalillari Arxivi</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Kategoriya: <b>{category_label}</b>\n"
            f"Jami: <b>{total}</b> ta dalil | "
            f"Sahifa: {page + 1}/{max(1, (total + FORENSICS_PAGE_SIZE - 1) // FORENSICS_PAGE_SIZE)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Batafsil ko'rish uchun dalilni tanlang:",
            parse_mode="HTML",
            reply_markup=forensics_list_kb(window, page, has_prev, has_next, category),
        )

    async def bulk_forensics_export(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        
        # forensiclist_pdf_{category} or forensiclist_docx_{category}
        parts = call.data.split("_")
        fmt = parts[0].replace("forensiclist", "")  # pdf or docx
        category = parts[1] if len(parts) > 1 else "all"
        
        category_lbl = {
            "extremism": "Diniy Ekstremizm",
            "drugs": "Giyohvandlik va Jargonlar",
            "bullying": "Kiberbulling va Haqorat",
            "all": "Barcha Dalillar",
        }.get(category, "Tergov Dalillari")
        
        wait = await call.message.answer(f"⏳ {category_lbl} tergov bayonnomalari ro'yxati tayyorlanmoqda...")
        
        if category == "all":
            cases = c.forensics.list_all(limit=1000)
        else:
            cases = c.forensics.list_filtered(category, limit=1000)
            
        if not cases:
            try:
                await wait.delete()
            except Exception:
                pass
            await call.answer("Ushbu turdagi qonunbuzarliklar ro'yxati bo'sh!", show_alert=True)
            return
            
        try:
            if fmt == "pdf":
                path = c.exporter.forensic_list_pdf(cases, category_lbl)
                fname = f"forensics_{category}_{datetime.now():%d%m%Y}.pdf"
                caption = f"📄 Kiber-Tergov Dalillari — {category_lbl} (PDF)"
            else:
                path = c.exporter.forensic_list_docx(cases, category_lbl)
                fname = f"forensics_{category}_{datetime.now():%d%m%Y}.docx"
                caption = f"📝 Kiber-Tergov Dalillari — {category_lbl} (DOCX)"
                
            await bot.send_document(
                call.from_user.id, FSInputFile(path, filename=fname), caption=caption,
            )
            os.unlink(path)
        except Exception as e:
            logger.error("Bulk forensics export xato: %s", e)
            await call.message.answer(f"❌ Xatolik: {e}")
        try:
            await wait.delete()
        except Exception:
            pass
        await call.answer()

    # Admin-only commands — filter does the gate, ADMIN_ONLY shows on miss
    dp.message.register(cmd_users, Command("users"), is_admin)
    dp.message.register(cmd_users_denied, Command("users"))
    dp.message.register(cmd_stats, Command("stats"), is_admin)
    dp.message.register(cmd_users_denied, Command("stats"))
    dp.message.register(cmd_broadcast, Command("broadcast"), is_admin)
    dp.message.register(cmd_users_denied, Command("broadcast"))

    dp.message.register(broadcast_cancel, BroadcastState.waiting_message, Command("cancel"))
    dp.message.register(broadcast_send, BroadcastState.waiting_message)

    dp.callback_query.register(handle_users_export, F.data.in_({"export_pdf", "export_docx"}))
    dp.callback_query.register(
        handle_groups_export, F.data.in_({"groups_export_pdf", "groups_export_docx"})
    )

    # State Sync & Forensics callbacks
    dp.callback_query.register(admin_state_sync, F.data == "admin_state_sync")
    dp.callback_query.register(admin_forensics_list, F.data.startswith("admin_forensics_list_p"))
    dp.callback_query.register(forensic_case_view, F.data.startswith("forensic_case_"))
    dp.callback_query.register(forensic_export, F.data.startswith("forensic_pdf_") | F.data.startswith("forensic_docx_"))
    dp.callback_query.register(forensic_delete, F.data.startswith("forensic_del_"))
    dp.callback_query.register(bulk_forensics_export, F.data.startswith("forensiclist_"))
