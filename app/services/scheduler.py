"""Background scheduler service for daily auto-backups and kiber-tips."""
import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile

from app.container import Container
from app.services.tips_service import TipsService

logger = logging.getLogger(__name__)


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



async def run_daily_tip(bot: Bot, container: Container) -> None:
    tips_service = TipsService()
    tip = tips_service.get_random_tip()
    active_groups = container.groups.active()
    
    logger.info(f"Kun maslahatini {len(active_groups)} ta aktiv guruhga yuborish boshlanmoqda...")
    for group in active_groups:
        try:
            await bot.send_message(
                group.chat_id,
                tip,
                parse_mode="HTML"
            )
            # Sleep briefly between messages to avoid flooding limits
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Guruhga ({group.chat_id}) kun maslahatini yuborishda xatolik: {e}")


async def scheduler_task(bot: Bot, container: Container) -> None:
    logger.info("⏳ SafeGuard fon rejalashtirgichi (background scheduler) ishga tushdi!")
    
    # We wait 10 seconds after startup to perform the initial startup backup (so we don't slow down startup)
    await asyncio.sleep(10)
    await run_daily_backup(bot, container)
    
    while True:
        try:
            # Sleep for 24 hours (86400 seconds)
            await asyncio.sleep(86400)
            
            logger.info("⏰ Kunlik fon topshiriqlari ishga tushmoqda...")
            # 1. Database Auto-Backup
            await run_daily_backup(bot, container)
            
            # 2. Daily Security Tip
            await run_daily_tip(bot, container)
            
        except asyncio.CancelledError:
            logger.info("Scheduler task bekor qilindi.")
            break
        except Exception as e:
            logger.error(f"Scheduler taskda kutilmagan xatolik: {e}")
            await asyncio.sleep(60) # Retry after 1 minute if it fails catastrophically


def start_scheduler(bot: Bot, container: Container) -> None:
    asyncio.create_task(scheduler_task(bot, container))
