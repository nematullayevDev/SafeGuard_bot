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
            language=row[7] if len(row) > 7 else "uz",
        )

    def save(self, user_id: int, first_name: str, username: str, phone: str, language: str = "uz", referred_by: int = 0) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, first_name, username, phone, registered_at, language, referred_by, referral_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    username = excluded.username,
                    phone = excluded.phone,
                    language = excluded.language
                """,
                (user_id, first_name, username or "", phone,
                 datetime.now().strftime("%d.%m.%Y %H:%M"), language, referred_by),
            )

    def is_registered(self, user_id: int) -> bool:
        with get_conn() as conn:
            return conn.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
            ).fetchone() is not None

    def all(self) -> list[User]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT user_id, first_name, username, phone, registered_at, quiz_passed, quiz_score, language "
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

    def get_language(self, user_id: int) -> str:
        with get_conn() as conn:
            row = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return row[0] if row and row[0] else "uz"

    def set_language(self, user_id: int, lang: str) -> None:
        with get_conn() as conn:
            conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))

    def get_referred_count(self, user_id: int) -> int:
        with get_conn() as conn:
            row = conn.execute("SELECT referral_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else 0
