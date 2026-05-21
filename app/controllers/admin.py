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
from app.views.keyboards import users_export_kb
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
