from datetime import datetime

from app.models import BannedSite
from app.repositories.base import BaseRepository, get_conn


class BannedSiteRepository(BaseRepository):
    @staticmethod
    def _row_to_site(row) -> BannedSite:
        return BannedSite(
            id=row[0],
            platform=row[1],
            name=row[2],
            added_at=row[3] or "",
            is_new=bool(row[4]),
        )

    def for_platform(self, platform: str) -> list[BannedSite]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, platform, name, added_at, is_new FROM banned_sites "
                "WHERE platform = ? ORDER BY id ASC",
                (platform,),
            ).fetchall()
        return [self._row_to_site(r) for r in rows]

    def add(self, platform: str, name: str) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO banned_sites (platform, name, added_at, is_new) VALUES (?, ?, ?, 1)",
                (platform, name, datetime.now().strftime("%d.%m.%Y %H:%M")),
            )
            return cur.lastrowid

    def delete(self, site_id: int) -> None:
        with get_conn() as conn:
            conn.execute("DELETE FROM banned_sites WHERE id = ?", (site_id,))

    def get(self, site_id: int) -> BannedSite | None:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, platform, name, added_at, is_new FROM banned_sites WHERE id = ?",
                (site_id,),
            ).fetchone()
        return self._row_to_site(row) if row else None

    def count(self, platform: str) -> int:
        with get_conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM banned_sites WHERE platform = ?", (platform,)
            ).fetchone()[0]
