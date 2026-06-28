import hashlib
from datetime import datetime, timedelta
from app.repositories.base import BaseRepository, get_conn

class AiCacheRepository(BaseRepository):
    @staticmethod
    def hash_text(normalized_text: str) -> str:
        return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    def get(self, text_hash: str, max_age_days: int = 7) -> dict | None:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT is_violation, category, reason, cached_at FROM ai_text_cache WHERE text_hash = ?",
                (text_hash,)
            ).fetchone()
        if not row:
            return None
        is_violation, category, reason, cached_at = row
        try:
            cached_dt = datetime.strptime(cached_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
            
        if datetime.now() - cached_dt > timedelta(days=max_age_days):
            return None
        with get_conn() as conn:
            conn.execute("UPDATE ai_text_cache SET hit_count = hit_count + 1 WHERE text_hash = ?", (text_hash,))
        return {"is_violation": bool(is_violation), "category": category, "reason": reason}

    def set(self, text_hash: str, is_violation: bool, category: str | None, reason: str) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO ai_text_cache (text_hash, is_violation, category, reason, cached_at, hit_count) "
                "VALUES (?, ?, ?, ?, ?, 1) "
                "ON CONFLICT(text_hash) DO UPDATE SET is_violation=excluded.is_violation, "
                "category=excluded.category, reason=excluded.reason, cached_at=excluded.cached_at",
                (text_hash, int(is_violation), category, reason,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
