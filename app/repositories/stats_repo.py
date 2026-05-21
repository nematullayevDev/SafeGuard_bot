from datetime import datetime

from app.models import BotStats
from app.repositories.base import BaseRepository, get_conn


class StatsRepository(BaseRepository):
    def get(self) -> BotStats:
        with get_conn() as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_scans = conn.execute("SELECT COUNT(*) FROM scan_history").fetchone()[0]
            dangerous = conn.execute(
                "SELECT COUNT(*) FROM scan_history WHERE result = 'xavfli'"
            ).fetchone()[0]
            suspicious = conn.execute(
                "SELECT COUNT(*) FROM scan_history WHERE result = 'shubhali'"
            ).fetchone()[0]
            bl_count = conn.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0]
            today = datetime.now().strftime("%d.%m.%Y")
            today_users = conn.execute(
                "SELECT COUNT(*) FROM users WHERE registered_at LIKE ?", (today + "%",)
            ).fetchone()[0]

        return BotStats(
            total_users=total_users,
            today_users=today_users,
            total_scans=total_scans,
            dangerous=dangerous,
            suspicious=suspicious,
            bl_count=bl_count,
        )
