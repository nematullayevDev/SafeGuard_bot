from datetime import datetime

from app.models import Group
from app.repositories.base import BaseRepository, get_conn


class GroupRepository(BaseRepository):
    @staticmethod
    def _row_to_group(row) -> Group:
        return Group(
            chat_id=row[0],
            title=row[1] or "",
            username=row[2] or "",
            is_active=bool(row[3]),
            added_at=row[4] or "",
        )

    def save(self, chat_id: int, title: str, username: str) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO groups (chat_id, title, username, is_active, added_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    title = excluded.title,
                    username = excluded.username,
                    is_active = 1,
                    added_at = excluded.added_at
                """,
                (chat_id, title, username or "",
                 datetime.now().strftime("%d.%m.%Y %H:%M")),
            )

    def update_info(self, chat_id: int, title: str, username: str) -> None:
        """Guruh nomi yoki username o'zgarganida yangilaydi."""
        with get_conn() as conn:
            conn.execute(
                "UPDATE groups SET title = ?, username = ? WHERE chat_id = ?",
                (title, username or "", chat_id),
            )

    def deactivate(self, chat_id: int) -> None:
        with get_conn() as conn:
            conn.execute("UPDATE groups SET is_active = 0 WHERE chat_id = ?", (chat_id,))

    def all(self) -> list[Group]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT chat_id, title, username, is_active, added_at "
                "FROM groups ORDER BY added_at DESC"
            ).fetchall()
        return [self._row_to_group(r) for r in rows]

    def active(self) -> list[Group]:
        return [g for g in self.all() if g.is_active]
