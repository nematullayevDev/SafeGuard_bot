from datetime import datetime
from app.models.forensic import ForensicCase
from app.repositories.base import BaseRepository, get_conn


class ForensicRepository(BaseRepository):
    @staticmethod
    def _row_to_case(row) -> ForensicCase:
        return ForensicCase(
            id=row[0],
            chat_id=row[1],
            chat_title=row[2] or "Guruh",
            user_id=row[3],
            full_name=row[4] or "Noma'lum",
            username=row[5] or "",
            phone=row[6] or "",
            message_text=row[7] or "",
            violation_type=row[8],
            reason=row[9] or "",
            detected_at=row[10] or "",
            photo_path=row[11]
        )

    def save(
        self,
        chat_id: int,
        chat_title: str,
        user_id: int,
        full_name: str,
        username: str,
        phone: str,
        message_text: str,
        violation_type: str,
        reason: str,
        photo_path: str | None = None
    ) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO forensics (
                    chat_id, chat_title, user_id, full_name, username, phone,
                    message_text, violation_type, reason, detected_at, photo_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id,
                    chat_title,
                    user_id,
                    full_name or "Noma'lum",
                    username or "",
                    phone or "",
                    message_text or "",
                    violation_type,
                    reason,
                    datetime.now().strftime("%d.%m.%Y %H:%M"),
                    photo_path
                )
            )
            return cur.lastrowid

    def get(self, case_id: int) -> ForensicCase | None:
        with get_conn() as conn:
            row = conn.execute(
                """
                SELECT id, chat_id, chat_title, user_id, full_name, username, phone,
                       message_text, violation_type, reason, detected_at, photo_path
                FROM forensics WHERE id = ?
                """,
                (case_id,)
            ).fetchone()
        return self._row_to_case(row) if row else None

    def list_all(self, limit: int = 50) -> list[ForensicCase]:
        with get_conn() as conn:
            rows = conn.execute(
                f"""
                SELECT id, chat_id, chat_title, user_id, full_name, username, phone,
                       message_text, violation_type, reason, detected_at, photo_path
                FROM forensics ORDER BY id DESC LIMIT {limit}
                """
            ).fetchall()
        return [self._row_to_case(r) for r in rows]

    def list_filtered(self, violation_type: str, limit: int = 50) -> list[ForensicCase]:
        with get_conn() as conn:
            rows = conn.execute(
                f"""
                SELECT id, chat_id, chat_title, user_id, full_name, username, phone,
                       message_text, violation_type, reason, detected_at, photo_path
                FROM forensics WHERE violation_type = ? ORDER BY id DESC LIMIT {limit}
                """,
                (violation_type,)
            ).fetchall()
        return [self._row_to_case(r) for r in rows]

    def delete(self, case_id: int) -> None:
        with get_conn() as conn:
            conn.execute("DELETE FROM forensics WHERE id = ?", (case_id,))

    def count(self) -> int:
        with get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM forensics").fetchone()[0]
