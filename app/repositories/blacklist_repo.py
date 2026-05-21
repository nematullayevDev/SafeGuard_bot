from datetime import datetime

from app.repositories.base import BaseRepository, get_conn


class BlacklistRepository(BaseRepository):
    def add(self, value: str) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO blacklist (value, added_at) VALUES (?, ?)",
                (value, datetime.now().strftime("%d.%m.%Y %H:%M")),
            )

    def remove(self, value: str) -> None:
        with get_conn() as conn:
            conn.execute("DELETE FROM blacklist WHERE value = ?", (value,))

    def exists(self, value: str) -> bool:
        with get_conn() as conn:
            return conn.execute(
                "SELECT 1 FROM blacklist WHERE value = ?", (value,)
            ).fetchone() is not None

    def recent(self, limit: int = 20) -> tuple[list[tuple[str, str]], int]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT value, added_at FROM blacklist ORDER BY added_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            count = conn.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0]
        return rows, count

    def clear(self) -> None:
        with get_conn() as conn:
            conn.execute("DELETE FROM blacklist")
