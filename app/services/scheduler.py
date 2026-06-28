"""Background scheduler service for daily auto-backups and kiber-tips."""
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from app.container import Container
from app.repositories.base import get_conn
from app.core.config import settings
from app.services.tips_service import TipsService

logger = logging.getLogger(__name__)

# O'zbekiston vaqt zonasi: UTC+5
UZB_TZ = timezone(timedelta(hours=5))

# Maslahat yuborish soati (O'zbekiston vaqti bo'yicha)
TIP_HOUR = 9    # 09:00
TIP_MINUTE = 0

# Backup yuborish soati (O'zbekiston vaqti bo'yicha)
BACKUP_HOUR = 2   # 02:00 (kecha)
BACKUP_MINUTE = 0


def _seconds_until(hour: int, minute: int) -> float:
    """Keyingi kun belgilangan soatgacha necha sekund qolganini hisoblaydi."""
    now = datetime.now(UZB_TZ)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        # Bugun o'tib ketgan — ertaga
        target = target + timedelta(days=1)
    delta = (target - now).total_seconds()
    return delta


async def run_daily_backup(bot: Bot, container: Container) -> None:
    from app.core.config import settings
    if not settings.admin_id:
        return
    db_file = os.path.join(settings.base_dir, "users.db")
    if not os.path.exists(db_file):
        logger.warning("Auto-Backup: users.db topilmadi!")
        return
    try:
        backup_path = container.exporter.db_backup(db_file)
        await bot.send_document(
            settings.admin_id,
            FSInputFile(backup_path, filename=f"users_autobackup_{datetime.now():%d%m%Y}.db"),
            caption="💾 <b>Kunlik Avtomatik Ma'lumotlar Bazasi Zaxira Nusxasi (Auto-Backup)</b>",
            parse_mode="HTML"
        )
        os.unlink(backup_path)
        logger.info("Auto-Backup muvaffaqiyatli jo'natildi!")
    except Exception as e:
        logger.error(f"Auto-Backup xatolik: {e}")


_tips_service = TipsService()


async def run_daily_tip(bot: Bot, container: Container) -> None:
    tip = _tips_service.get_daily_tip()

    # 1. Barcha foydalanuvchilarga yuborish
    users = container.users.all()
    logger.info(f"Kun maslahatini {len(users)} ta foydalanuvchiga yuborish boshlanmoqda...")
    for user in users:
        try:
            await bot.send_message(user.user_id, tip, parse_mode="HTML")
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Foydalanuvchiga ({user.user_id}) maslahat yuborishda xatolik: {e}")

    # 2. Barcha aktiv guruhlarga yuborish
    active_groups = container.groups.active()
    logger.info(f"Kun maslahatini {len(active_groups)} ta aktiv guruhga yuborish boshlanmoqda...")
    for group in active_groups:
        try:
            await bot.send_message(group.chat_id, tip, parse_mode="HTML")
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Guruhga ({group.chat_id}) maslahat yuborishda xatolik: {e}")


async def _backup_loop(bot: Bot, container: Container) -> None:
    """Har kuni soat 02:00 (O'zbekiston) da backup yuboradi."""
    # Ishga tushganda bir marta backup qilish (10 sekund kutib)
    await asyncio.sleep(10)
    await run_daily_backup(bot, container)

    while True:
        try:
            wait = _seconds_until(BACKUP_HOUR, BACKUP_MINUTE)
            logger.info(f"⏰ Keyingi backup: {wait/3600:.1f} soatdan keyin (02:00 UZB)")
            await asyncio.sleep(wait)
            await run_daily_backup(bot, container)
        except asyncio.CancelledError:
            logger.info("Backup loop bekor qilindi.")
            break
        except Exception as e:
            logger.error(f"Backup loopda xatolik: {e}")
            await asyncio.sleep(60)


async def _tip_loop(bot: Bot, container: Container) -> None:
    """Har kuni soat 09:00 (O'zbekiston) da maslahat yuboradi."""
    while True:
        try:
            wait = _seconds_until(TIP_HOUR, TIP_MINUTE)
            logger.info(f"💡 Keyingi maslahat: {wait/3600:.1f} soatdan keyin (09:00 UZB)")
            await asyncio.sleep(wait)
            logger.info("⏰ Kunlik maslahat yuborilmoqda...")
            await run_daily_tip(bot, container)
async def _premium_expiration_loop(bot: Bot, container: Container) -> None:
    """Checks for active premium subscriptions that expire soon or have expired."""
    while True:
        try:
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            one_hour_later_str = (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

            # Get owner link for warning messages
            owner_url = "https://t.me/webdragon"
            with get_conn() as conn:
                owner_row = conn.execute("SELECT username FROM users WHERE user_id = ?", (settings.admin_id,)).fetchone()
            if owner_row and owner_row[0]:
                owner_url = f"https://t.me/{owner_row[0].lstrip('@')}"

            # ── 1. Expired Users cleanup ──
            with get_conn() as conn:
                expired_users = conn.execute(
                    "SELECT user_id FROM user_subscriptions WHERE plan = 'premium' AND expires_at < ?",
                    (now_str,)
                ).fetchall()
                for r in expired_users:
                    uid = r[0]
                    conn.execute(
                        "UPDATE user_subscriptions SET plan = 'free', expires_at = NULL, warning_sent = 0 WHERE user_id = ?",
                        (uid,)
                    )
                    user_lang = container.users.get_language(uid)
                    exp_msg = {
                        "uz": "⚠️ <b>SafeGuard Premium muddati tugadi!</b>\n\nGuruhlardagi kiber-tahlil limiti va barcha premium imkoniyatlar Free (bepul) rejasiga qaytarildi.",
                        "uz_cyr": "⚠️ <b>SafeGuard Премиум муддати тугади!</b>\n\nГуруҳлардаги кибер-таҳлил лимити ва барча премиум имкониятлар Free (бепул) режасига қайтарилди.",
                        "ru": "⚠️ <b>Срок действия SafeGuard Premium истек!</b>\n\nЛимит ИИ-анализа в группах и все функции Premium были возвращены к тарифу Free (бесплатно).",
                        "en": "⚠️ <b>SafeGuard Premium has expired!</b>\n\nYour group AI analysis limit and all Premium features have been reverted to the Free plan."
                    }.get(user_lang, "⚠️ SafeGuard Premium expired")
                    try:
                        await bot.send_message(uid, exp_msg, parse_mode="HTML")
                    except Exception:
                        pass

            # ── 2. Expiring Users 1-hour warning ──
            with get_conn() as conn:
                expiring_users = conn.execute(
                    "SELECT user_id, expires_at FROM user_subscriptions "
                    "WHERE plan = 'premium' AND expires_at >= ? AND expires_at <= ? AND warning_sent = 0",
                    (now_str, one_hour_later_str)
                ).fetchall()
                for r in expiring_users:
                    uid = r[0]
                    user_lang = container.users.get_language(uid)
                    text = {
                        "uz": "⚠️ <b>SafeGuard Premium obunangiz 1 soatdan keyin o'chadi.</b>\n\nUni yana faollashtirasizmi?",
                        "uz_cyr": "⚠️ <b>SafeGuard Премиум обунангиз 1 соатдан кейин ўчади.</b>\n\nУни яна фаоллаштирасизми?",
                        "ru": "⚠️ <b>Ваша подписка SafeGuard Premium истекает через 1 час.</b>\n\nХотите продлить её?",
                        "en": "⚠️ <b>Your SafeGuard Premium subscription will expire in 1 hour.</b>\n\nWould you like to reactivate it?"
                    }.get(user_lang, "⚠️ SafeGuard Premium expiring")

                    btn_yes = {"uz": "Ha ✅", "uz_cyr": "Ҳа ✅", "ru": "Да ✅", "en": "Yes ✅"}.get(user_lang, "Yes")
                    btn_no = {"uz": "Yo'q ❌", "uz_cyr": "Йўқ ❌", "ru": "Нет ❌", "en": "No ❌"}.get(user_lang, "No")

                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text=btn_yes, url=owner_url),
                            InlineKeyboardButton(text=btn_no, callback_data="go_start")
                        ]
                    ])
                    try:
                        await bot.send_message(uid, text, reply_markup=kb, parse_mode="HTML")
                        conn.execute("UPDATE user_subscriptions SET warning_sent = 1 WHERE user_id = ?", (uid,))
                    except Exception:
                        pass

            # ── 3. Expired Groups cleanup ──
            with get_conn() as conn:
                expired_groups = conn.execute(
                    "SELECT chat_id FROM group_subscriptions WHERE plan = 'premium' AND expires_at < ?",
                    (now_str,)
                ).fetchall()
                for r in expired_groups:
                    chat_id = r[0]
                    conn.execute(
                        "UPDATE group_subscriptions SET plan = 'free', expires_at = NULL, warning_sent = 0 WHERE chat_id = ?",
                        (chat_id,)
                    )
                    g_settings = container.groups.get_custom_settings(chat_id)
                    g_lang = g_settings.get("language", "uz")
                    exp_msg = {
                        "uz": "⚠️ <b>Guruh Premium obuna muddati tugadi!</b>\n\nKiber-tahlil limiti va xavfsizlik modullari Free (bepul) rejasiga qaytarildi.",
                        "uz_cyr": "⚠️ <b>Гуруҳ Премиум обуна муддати тугади!</b>\n\nКибер-таҳлил лимити ва хавфсизлик модуллари Free (бепул) режасига қайтарилди.",
                        "ru": "⚠️ <b>Срок действия Premium подписки группы истек!</b>\n\nЛимит анализа и модули безопасности возвращены к бесплатному тарифу.",
                        "en": "⚠️ <b>Group Premium subscription has expired!</b>\n\nSecurity analysis limits and modules have been reverted to the Free plan."
                    }.get(g_lang, "⚠️ Group Premium Expired")
                    try:
                        await bot.send_message(chat_id, exp_msg, parse_mode="HTML")
                    except Exception:
                        pass

            # ── 4. Expiring Groups 1-hour warning ──
            with get_conn() as conn:
                expiring_groups = conn.execute(
                    "SELECT chat_id, expires_at FROM group_subscriptions "
                    "WHERE plan = 'premium' AND expires_at >= ? AND expires_at <= ? AND warning_sent = 0",
                    (now_str, one_hour_later_str)
                ).fetchall()
                for r in expiring_groups:
                    chat_id = r[0]
                    g_settings = container.groups.get_custom_settings(chat_id)
                    g_lang = g_settings.get("language", "uz")
                    text = {
                        "uz": "⚠️ <b>SafeGuard Premium obunasi 1 soatdan keyin o'chadi.</b>\n\nUni yana faollashtirish uchun guruh yaratuvchisi administratorga murojaat qilishi mumkin.",
                        "uz_cyr": "⚠️ <b>SafeGuard Премиум обунаси 1 соатдан кейин ўчади.</b>\n\nУни яна фаоллаштириш учун гуруҳ яратувчиси администраторга мурожаат қилиши мумкин.",
                        "ru": "⚠️ <b>Подписка SafeGuard Premium в этой группе истекает через 1 час.</b>\n\nДля продления создатель группы может связаться с администратором.",
                        "en": "⚠️ <b>SafeGuard Premium for this group will expire in 1 hour.</b>\n\nTo reactivate, the group creator can contact the admin."
                    }.get(g_lang, "⚠️ Group Premium expiring")

                    btn_yes = {"uz": "Ha ✅", "uz_cyr": "Ҳа ✅", "ru": "Да ✅", "en": "Yes ✅"}.get(g_lang, "Yes")
                    btn_no = {"uz": "Yo'q ❌", "uz_cyr": "Йўқ ❌", "ru": "Нет ❌", "en": "No ❌"}.get(g_lang, "No")

                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text=btn_yes, url=owner_url),
                            InlineKeyboardButton(text=btn_no, callback_data="go_start")
                        ]
                    ])
                    try:
                        await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
                        conn.execute("UPDATE group_subscriptions SET warning_sent = 1 WHERE chat_id = ?", (chat_id,))
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Error in premium expiration loop: {e}")

        await asyncio.sleep(300) # every 5 minutes


def start_scheduler(bot: Bot, container: Container) -> None:
    logger.info("⏳ SafeGuard fon rejalashtirgichi ishga tushdi!")
    logger.info(f"   📦 Backup: har kuni 02:00 (O'zbekiston)")
    logger.info(f"   💡 Maslahat: har kuni 09:00 (O'zbekiston)")
    logger.info(f"   💎 Premium monitoring: har 5 daqiqada")
    asyncio.create_task(_backup_loop(bot, container))
    asyncio.create_task(_tip_loop(bot, container))
    asyncio.create_task(_premium_expiration_loop(bot, container))
