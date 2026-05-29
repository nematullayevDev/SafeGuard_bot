"""Background scheduler service for daily auto-backups and kiber-tips."""
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.types import FSInputFile

from app.container import Container
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
    active_groups = container.groups.active()

    logger.info(f"Kun maslahatini {len(active_groups)} ta aktiv guruhga yuborish boshlanmoqda...")
    for group in active_groups:
        try:
            await bot.send_message(group.chat_id, tip, parse_mode="HTML")
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Guruhga ({group.chat_id}) kun maslahatini yuborishda xatolik: {e}")


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
        except asyncio.CancelledError:
            logger.info("Tip loop bekor qilindi.")
            break
        except Exception as e:
            logger.error(f"Tip loopda xatolik: {e}")
            await asyncio.sleep(60)


def start_scheduler(bot: Bot, container: Container) -> None:
    logger.info("⏳ SafeGuard fon rejalashtirgichi ishga tushdi!")
    logger.info(f"   📦 Backup: har kuni 02:00 (O'zbekiston)")
    logger.info(f"   💡 Maslahat: har kuni 09:00 (O'zbekiston)")
    asyncio.create_task(_backup_loop(bot, container))
    asyncio.create_task(_tip_loop(bot, container))
