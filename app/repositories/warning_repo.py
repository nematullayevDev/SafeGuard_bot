from datetime import datetime

from app.repositories.base import BaseRepository, get_conn


class WarningRepository(BaseRepository):
    def add(self, chat_id: int, user_id: int, reason: str) -> int:
        """Insert a warning and return the user's total warn count in this chat."""
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO warnings (chat_id, user_id, reason, warned_at) VALUES (?, ?, ?, ?)",
                (chat_id, user_id, reason,
                 datetime.now().strftime("%d.%m.%Y %H:%M")),
            )
            return conn.execute(
                "SELECT COUNT(*) FROM warnings WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id),
            ).fetchone()[0]

    def count(self, chat_id: int, user_id: int) -> int:
        with get_conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM warnings WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id),
            ).fetchone()[0]

    def clear(self, chat_id: int, user_id: int) -> None:
        with get_conn() as conn:
            conn.execute(
                "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id),
            )
