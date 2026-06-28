from datetime import datetime, timedelta
from app.repositories.base import BaseRepository, get_conn

class UrlCacheRepository(BaseRepository):
    def get(self, url: str, max_age_hours: int = 24) -> dict | None:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT verdict, malicious, suspicious, harmless, undetected, checked_at "
                "FROM url_scan_cache WHERE url = ?", (url,)
            ).fetchone()
        if not row:
            return None
        verdict, mal, sus, har, und, checked_at = row
        try:
            checked_dt = datetime.strptime(checked_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
            
        # DANGEROUS results are cached indefinitely, others expire after max_age_hours
        if verdict != "DANGEROUS" and datetime.now() - checked_dt > timedelta(hours=max_age_hours):
            return None
        return {"verdict": verdict, "malicious": mal, "suspicious": sus,
                "harmless": har, "undetected": und}

    def set(self, url: str, verdict: str, malicious: int, suspicious: int,
            harmless: int, undetected: int) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO url_scan_cache (url, verdict, malicious, suspicious, harmless, undetected, checked_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(url) DO UPDATE SET verdict=excluded.verdict, malicious=excluded.malicious, "
                "suspicious=excluded.suspicious, harmless=excluded.harmless, undetected=excluded.undetected, "
                "checked_at=excluded.checked_at",
                (url, verdict, malicious, suspicious, harmless, undetected,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
