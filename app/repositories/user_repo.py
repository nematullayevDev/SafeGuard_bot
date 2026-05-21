from datetime import datetime

from app.models import User
from app.repositories.base import BaseRepository, get_conn


class UserRepository(BaseRepository):
    @staticmethod
    def _row_to_user(row) -> User:
        return User(
            user_id=row[0],
            first_name=row[1] or "",
            username=row[2] or "",
            phone=row[3] or "",
            registered_at=row[4] or "",
        )

    def save(self, user_id: int, first_name: str, username: str, phone: str) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO users (user_id, first_name, username, phone, registered_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, first_name, username or "", phone,
                 datetime.now().strftime("%d.%m.%Y %H:%M")),
            )

    def is_registered(self, user_id: int) -> bool:
        with get_conn() as conn:
            return conn.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
            ).fetchone() is not None

    def all(self) -> list[User]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT user_id, first_name, username, phone, registered_at "
                "FROM users ORDER BY registered_at DESC"
            ).fetchall()
        return [self._row_to_user(r) for r in rows]

    def all_ids(self) -> list[int]:
        with get_conn() as conn:
            return [r[0] for r in conn.execute("SELECT user_id FROM users").fetchall()]
