from datetime import datetime

from app.models import Group
from app.repositories.base import BaseRepository, get_conn


class GroupRepository(BaseRepository):
    # RAM da kesh — {chat_id: (title, username)}
    # Bazaga faqat o'zgarish bo'lganda yoziladi
    _cache: dict[int, tuple[str, str]] = {}

    @staticmethod
    def _row_to_group(row) -> Group:
        return Group(
            chat_id=row[0],
            title=row[1] or "",
            username=row[2] or "",
            is_active=bool(row[3]),
            added_at=row[4] or "",
            invite_link=row[5] or "",
        )

    def save(self, chat_id: int, title: str, username: str, invite_link: str = "", added_by: int = 0) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO groups (chat_id, title, username, is_active, added_at, invite_link, added_by)
                VALUES (?, ?, ?, 1, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    title = excluded.title,
                    username = excluded.username,
                    is_active = 1,
                    added_at = excluded.added_at,
                    invite_link = excluded.invite_link,
                    added_by = CASE WHEN excluded.added_by != 0 THEN excluded.added_by ELSE added_by END
                """,
                (chat_id, title, username or "",
                 datetime.now().strftime("%d.%m.%Y %H:%M"),
                 invite_link or "", added_by),
            )

    def active_by_user(self, user_id: int) -> list:
        """Faqat shu foydalanuvchi qo'shgan aktiv guruhlar."""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT chat_id, title, username, is_active, added_at, COALESCE(invite_link,'') "
                "FROM groups WHERE is_active = 1 AND added_by = ? ORDER BY added_at DESC",
                (user_id,)
            ).fetchall()
        return [self._row_to_group(r) for r in rows]

    def update_info(self, chat_id: int, title: str, username: str, invite_link: str = "") -> None:
        """Guruh nomi yoki username o'zgarganida yangilaydi.
        
        Kesh orqali ishlaydi — bazaga faqat haqiqiy o'zgarish bo'lganda yozadi.
        100 ta odam yozsa ham bazaga 0 ta so'rov ketadi (agar nom o'zgarmagan bo'lsa).
        """
        cached = self._cache.get(chat_id)
        if cached == (title, username):
            # Nom o'zgarmagan — bazaga yozmasdan qaytamiz
            return

        # O'zgarish bor — bazani yangilaymiz
        with get_conn() as conn:
            conn.execute(
                """UPDATE groups SET title = ?, username = ?,
                   invite_link = CASE WHEN ? != '' THEN ? ELSE invite_link END
                   WHERE chat_id = ?""",
                (title, username or "", invite_link, invite_link, chat_id),
            )
        # Keshni yangilaymiz
        self._cache[chat_id] = (title, username)

    def deactivate(self, chat_id: int) -> None:
        with get_conn() as conn:
            conn.execute("UPDATE groups SET is_active = 0 WHERE chat_id = ?", (chat_id,))

    def all(self) -> list[Group]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT chat_id, title, username, is_active, added_at, COALESCE(invite_link,'') "
                "FROM groups ORDER BY added_at DESC"
            ).fetchall()
        return [self._row_to_group(r) for r in rows]

    def active(self) -> list[Group]:
        return [g for g in self.all() if g.is_active]
