from datetime import datetime

from app.models import HistoryEntry, ItemType, ScanVerdict
from app.repositories.base import BaseRepository, get_conn


class HistoryRepository(BaseRepository):
    def save(self, user_id: int, item_type: ItemType, value: str, verdict: ScanVerdict) -> None:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO scan_history (user_id, item_type, value, result, scanned_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, item_type.value, value, verdict.value,
                 datetime.now().strftime("%d.%m %H:%M")),
            )

    def recent(self, user_id: int, limit: int = 10) -> list[HistoryEntry]:
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT item_type, value, result, scanned_at FROM scan_history
                WHERE user_id = ? ORDER BY id DESC LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

        entries: list[HistoryEntry] = []
        for item_type, value, result, scanned_at in rows:
            try:
                it = ItemType(item_type)
            except ValueError:
                it = ItemType.LINK
            try:
                v = ScanVerdict(result)
            except ValueError:
                v = ScanVerdict.UNKNOWN
            entries.append(HistoryEntry(item_type=it, value=value,
                                        verdict=v, scanned_at=scanned_at or ""))
        return entries
