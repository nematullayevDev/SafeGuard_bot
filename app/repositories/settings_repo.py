from app.repositories.base import BaseRepository, get_conn


class SettingsRepository(BaseRepository):
    """User-level toggles. Group rows use chat_id (negative) as key — no collision with user IDs."""

    def get_spam_filter(self, user_id: int) -> bool:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT spam_filter FROM user_settings WHERE user_id = ?", (user_id,)
            ).fetchone()
        return bool(row[0]) if row else True

    def set_spam_filter(self, user_id: int, value: bool) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO user_settings (user_id, spam_filter) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET spam_filter = excluded.spam_filter
                """,
                (user_id, int(value)),
            )

    def get_group_mode(self, chat_id: int) -> bool:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT group_mode FROM user_settings WHERE user_id = ?", (chat_id,)
            ).fetchone()
        return bool(row[0]) if row else False

    def set_group_mode(self, chat_id: int, value: bool) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO user_settings (user_id, group_mode) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET group_mode = excluded.group_mode
                """,
                (chat_id, int(value)),
            )

    def get_group_settings(self, chat_id: int) -> dict:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT filter_links, filter_files, filter_nlp FROM user_settings WHERE user_id = ?",
                (chat_id,)
            ).fetchone()
        if row:
            return {
                "filter_links": bool(row[0]),
                "filter_files": bool(row[1]),
                "filter_nlp": bool(row[2])
            }
        return {
            "filter_links": True,
            "filter_files": True,
            "filter_nlp": True
        }

    def set_group_filter(self, chat_id: int, filter_name: str, value: bool) -> None:
        if filter_name not in ("filter_links", "filter_files", "filter_nlp"):
            return
        with get_conn() as conn:
            conn.execute(
                f"""
                INSERT INTO user_settings (user_id, {filter_name}) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET {filter_name} = excluded.{filter_name}
                """,
                (chat_id, int(value)),
            )
