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
            quiz_passed=row[5] if len(row) > 5 else 0,
            quiz_score=row[6] if len(row) > 6 else 0,
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
                "SELECT user_id, first_name, username, phone, registered_at, quiz_passed, quiz_score "
                "FROM users ORDER BY registered_at DESC"
            ).fetchall()
        return [self._row_to_user(r) for r in rows]

    def all_ids(self) -> list[int]:
        with get_conn() as conn:
            return [r[0] for r in conn.execute("SELECT user_id FROM users").fetchall()]

    def save_quiz_result(self, user_id: int, score: int, passed: bool) -> None:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET quiz_score = ?, quiz_passed = ? WHERE user_id = ?",
                (score, int(passed), user_id)
            )

    def get_quiz_status(self, user_id: int) -> dict:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT quiz_passed, quiz_score FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
        if row:
            return {"passed": bool(row[0]), "score": row[1]}
        return {"passed": False, "score": 0}
