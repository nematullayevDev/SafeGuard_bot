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

    # ─── Forensics Main Menu ──────────────────────────
    async def admin_forensics_main(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        from app.views.keyboards import forensics_main_menu
        await call.message.edit_text(
            "📂 <b>Kiber-Tergov Dalillari Arxivi</b>\n\n"
            "Gumondorlar ro'yxatini ko'rish uchun tegishli yo'nalishni tanlang:\n\n"
            "📌 Ma'lumotlar ochiq ma'lumotlar hamda tizim tahlili asosida shakllantirilgan.",
            reply_markup=forensics_main_menu(), parse_mode="HTML",
        )
        await call.answer()

    # ─── Forensics Suspects List ──────────────────────
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

        suspects = c.forensics.list_suspects_grouped(category)
        total = len(suspects)
        
        start = page * FORENSICS_PAGE_SIZE
        end = start + FORENSICS_PAGE_SIZE
        window = suspects[start:end]
        has_prev = page > 0
        has_next = end < total

        category_label = {
            "extremism": "🚨 Ekstremizm",
            "drugs": "💊 Giyohvandlik",
            "bullying": "⚠️ Kiberbulling",
            "cybercrime": "💻 Kiberjinoyat",
            "all": "🌐 Barcha dalillar",
        }.get(category, "Tergov")

        total_pages = max(1, (total + FORENSICS_PAGE_SIZE - 1) // FORENSICS_PAGE_SIZE)
        page_num = page + 1
        end_num = min(start + FORENSICS_PAGE_SIZE, total)
        text = formatters.forensics_list_text(category_label, total, page_num, total_pages, start + 1, end_num)

        await call.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=forensics_list_kb(window, page, has_prev, has_next, category),
        )
        await call.answer()

    async def forensic_suspect_view(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        # forensic_suspect_{user_id}_p{page}_c{category}
        raw = call.data.replace("forensic_suspect_", "")
        parts = raw.split("_p")
        try:
            user_id = int(parts[0])
            subparts = parts[1].split("_c")
            page = int(subparts[0])
            category = subparts[1] if len(subparts) > 1 else "all"
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        cases = c.forensics.get_suspect_cases(user_id)
        if not cases:
            await call.answer("Gumondor dalillari topilmadi!", show_alert=True)
            return

        first_case = cases[0]
        suspect_details = {
            "user_id": user_id,
            "full_name": first_case.full_name,
            "username": first_case.username,
            "phone": first_case.phone
        }

        await call.message.edit_text(
            formatters.forensic_suspect_detail(suspect_details, cases),
            parse_mode="HTML",
            reply_markup=forensic_detail_kb(user_id, page, category),
        )
        await call.answer()

    async def forensic_export(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        # forensic_pdf_{user_id} or forensic_docx_{user_id}
        parts = call.data.split("_")
        fmt = parts[1]  # pdf or docx
        try:
            user_id = int(parts[2])
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        cases = c.forensics.get_suspect_cases(user_id)
        if not cases:
            await call.answer("Dalillar topilmadi!", show_alert=True)
            return

        first_case = cases[0]
        suspect_details = {
            "user_id": user_id,
            "full_name": first_case.full_name,
            "username": first_case.username,
            "phone": first_case.phone
        }

        wait = await call.message.answer("⏳ Tergov bayonnomasi tayyorlanmoqda...")
        try:
            if fmt == "pdf":
                path = c.exporter.forensic_report_pdf(suspect_details, cases)
                fname = f"forensic_report_{user_id}_{datetime.now():%d%m%Y}.pdf"
                caption = f"📄 Tergov Bayonnomasi — Gumondor ID {user_id} (PDF)"
            else:
                path = c.exporter.forensic_report_docx(suspect_details, cases)
                fname = f"forensic_report_{user_id}_{datetime.now():%d%m%Y}.docx"
                caption = f"📝 Tergov Bayonnomasi — Gumondor ID {user_id} (DOCX)"
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
        # forensic_del_{user_id}_p{page}_c{category}
        raw = call.data.replace("forensic_del_", "")
        parts = raw.split("_p")
        try:
            user_id = int(parts[0])
            subparts = parts[1].split("_c")
            page = int(subparts[0])
            category = subparts[1] if len(subparts) > 1 else "all"
        except (ValueError, IndexError):
            await call.answer("Xatolik!", show_alert=True)
            return

        cases = c.forensics.get_suspect_cases(user_id)
        for case in cases:
            # Profil rasmini ham o'chirish
            if case.photo_path and os.path.exists(case.photo_path):
                try:
                    os.unlink(case.photo_path)
                except Exception:
                    pass

        c.forensics.delete_suspect_cases(user_id)
        await call.answer(f"✅ Gumondorga tegishli barcha dalillar o'chirildi!", show_alert=True)

        # Ro'yxatga qaytish
        suspects = c.forensics.list_suspects_grouped(category)
        total = len(suspects)
        start = page * FORENSICS_PAGE_SIZE
        end = start + FORENSICS_PAGE_SIZE
        window = suspects[start:end]
        has_prev = page > 0
        has_next = end < total

        category_label = {
            "extremism": "🚨 Ekstremizm",
            "drugs": "💊 Giyohvandlik",
            "bullying": "⚠️ Kiberbulling",
            "cybercrime": "💻 Kiberjinoyat",
            "all": "🌐 Barcha dalillar",
        }.get(category, "Tergov")

        if not suspects:
            await call.message.edit_text(
                f"📂 <b>Kiber-Tergov Dalillari Arxivi ({category_label})</b>\n\n📭 Arxiv bo'sh.",
                parse_mode="HTML",
                reply_markup=back_button("admin_panel"),
            )
            return

        total_pages = max(1, (total + FORENSICS_PAGE_SIZE - 1) // FORENSICS_PAGE_SIZE)
        page_num = page + 1
        end_num = min(start + FORENSICS_PAGE_SIZE, total)
        text = formatters.forensics_list_text(category_label, total, page_num, total_pages, start + 1, end_num)

        await call.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=forensics_list_kb(window, page, has_prev, has_next, category),
        )

    async def bulk_forensics_export(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        
        # forensiclist_pdf_{category} or forensiclist_docx_{category}
        parts = call.data.split("_")
        if len(parts) >= 3:
            fmt = parts[1]
            category = parts[2]
        else:
            fmt = parts[0].replace("forensiclist", "")
            category = parts[1] if len(parts) > 1 else "all"
        
        category_lbl = {
            "extremism": "Diniy Ekstremizm",
            "drugs": "Giyohvandlik va Jargonlar",
            "bullying": "Kiberbulling va Haqorat",
            "cybercrime": "Kiberjinoyat va Firibgarlik",
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

    async def cmd_backup(message: Message):
        if message.from_user.id != settings.admin_id:
            await message.answer(ADMIN_ONLY)
            return
        db_file = os.path.join(settings.base_dir, "users.db")
        if not os.path.exists(db_file):
            await message.answer("❌ Ma'lumotlar bazasi fayli topilmadi!")
            return
        try:
            backup_path = c.exporter.db_backup(db_file)
            await bot.send_document(
                message.from_user.id,
                FSInputFile(backup_path, filename=f"users_backup_{datetime.now():%d%m%Y_%H%M%S}.db"),
                caption="💾 <b>SafeGuard Baza Zaxira Nusxasi (Backup)</b>",
                parse_mode="HTML"
            )
            os.unlink(backup_path)
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

    async def handle_admin_backup(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        db_file = os.path.join(settings.base_dir, "users.db")
        if not os.path.exists(db_file):
            await call.answer("❌ Baza fayli topilmadi!", show_alert=True)
            return
        wait = await call.message.answer("⏳ Baza zaxiralanmoqda...")
        try:
            backup_path = c.exporter.db_backup(db_file)
            await bot.send_document(
                call.from_user.id,
                FSInputFile(backup_path, filename=f"users_backup_{datetime.now():%d%m%Y_%H%M%S}.db"),
                caption="💾 <b>SafeGuard Baza Zaxira Nusxasi (Backup)</b>",
                parse_mode="HTML"
            )
            os.unlink(backup_path)
            await call.answer("Baza muvaffaqiyatli zaxiralandi!")
        except Exception as e:
            logger.error(f"Backup export xato: {e}")
            await call.message.answer(f"❌ Xatolik: {e}")
        try:
            await wait.delete()
        except Exception:
            pass

    async def handle_admin_stats_pdf(call: CallbackQuery):
        if call.from_user.id != settings.admin_id:
            await call.answer(ADMIN_ONLY_ALERT, show_alert=True)
            return
        wait = await call.message.answer("⏳ PDF hisobot tayyorlanmoqda...")
        try:
            stats = c.stats.get()
            path = c.exporter.stats_pdf_report(stats)
            fname = f"stats_report_{datetime.now():%d%m%Y}.pdf"
            caption = "📊 <b>Tahliliy Statistika PDF Hisoboti</b>"
            await bot.send_document(
                call.from_user.id,
                FSInputFile(path, filename=fname),
                caption=caption,
                parse_mode="HTML"
            )
            os.unlink(path)
            await call.answer()
        except Exception as e:
            logger.error(f"Stats PDF export xato: {e}")
            await call.message.answer(f"❌ Xatolik: {e}")
        try:
            await wait.delete()
        except Exception:
            pass

    # Admin-only commands — filter does the gate, ADMIN_ONLY shows on miss
    dp.message.register(cmd_users, Command("users"), is_admin)
    dp.message.register(cmd_users_denied, Command("users"))
    dp.message.register(cmd_stats, Command("stats"), is_admin)
    dp.message.register(cmd_users_denied, Command("stats"))
    dp.message.register(cmd_backup, Command("backup"), is_admin)
    dp.message.register(cmd_users_denied, Command("backup"))
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
    dp.callback_query.register(admin_forensics_main, F.data == "admin_forensics_main")
    dp.callback_query.register(admin_forensics_list, F.data.startswith("admin_forensics_list_p"))
    dp.callback_query.register(forensic_suspect_view, F.data.startswith("forensic_suspect_"))
    dp.callback_query.register(forensic_export, F.data.startswith("forensic_pdf_") | F.data.startswith("forensic_docx_"))
    dp.callback_query.register(forensic_delete, F.data.startswith("forensic_del_"))
    dp.callback_query.register(bulk_forensics_export, F.data.startswith("forensiclist_"))
    dp.callback_query.register(handle_admin_backup, F.data == "admin_backup")
    dp.callback_query.register(handle_admin_stats_pdf, F.data == "admin_stats_pdf")

