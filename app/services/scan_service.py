"""Orchestrates VirusTotal scans into domain ScanResult + history persistence."""
import logging

from app.models import HistoryEntry, ItemType, ScanResult, ScanVerdict
from app.repositories import BlacklistRepository, HistoryRepository
from app.services.virustotal_service import VirusTotalService

logger = logging.getLogger(__name__)


def _classify(mal: int, sus: int) -> ScanVerdict:
    if mal >= 3:
        return ScanVerdict.DANGEROUS
    if mal >= 1 or sus >= 2:
        return ScanVerdict.SUSPICIOUS
    return ScanVerdict.SAFE


class ScanService:
    def __init__(self, vt: VirusTotalService,
                 history_repo: HistoryRepository,
                 blacklist_repo: BlacklistRepository) -> None:
        self._vt = vt
        self._history = history_repo
        self._blacklist = blacklist_repo

    async def scan_url(self, user_id: int, url: str) -> ScanResult:
        try:
            raw = await self._vt.scan_url(url)
            result = self._parse_url_result(url, raw)
        except Exception as e:
            logger.exception("URL scan xato: %s", url)
            return ScanResult(item_type=ItemType.LINK, value=url,
                              verdict=ScanVerdict.UNKNOWN, error=str(e))

        self._history.save(user_id, ItemType.LINK, url, result.verdict)
        if result.verdict is ScanVerdict.DANGEROUS:
            self._blacklist.add(url)
        return result

    async def scan_file(self, user_id: int, file_bytes: bytes, file_name: str) -> ScanResult:
        try:
            raw = await self._vt.scan_file(file_bytes, file_name)
            result = self._parse_file_result(file_name, raw)
        except Exception as e:
            logger.exception("File scan xato: %s", file_name)
            return ScanResult(item_type=ItemType.FILE, value=file_name,
                              verdict=ScanVerdict.UNKNOWN, error=str(e))

        self._history.save(user_id, ItemType.FILE, file_name, result.verdict)
        if result.verdict is ScanVerdict.DANGEROUS:
            self._blacklist.add(file_name)
        return result

    def history(self, user_id: int, limit: int = 10) -> list[HistoryEntry]:
        return self._history.recent(user_id, limit)

    # ── internal parsing ───────────────────────────────
    @staticmethod
    def _stats_from(attrs: dict) -> tuple[int, int, int, int]:
        stats = attrs.get("last_analysis_stats") or attrs.get("stats", {})
        return (
            stats.get("malicious", 0), stats.get("suspicious", 0),
            stats.get("harmless", 0), stats.get("undetected", 0),
        )

    def _parse_url_result(self, url: str, raw: dict) -> ScanResult:
        try:
            mal, sus, har, und = self._stats_from(raw["data"]["attributes"])
        except Exception:
            return ScanResult(item_type=ItemType.LINK, value=url,
                              verdict=ScanVerdict.UNKNOWN)
        return ScanResult(
            item_type=ItemType.LINK, value=url, verdict=_classify(mal, sus),
            malicious=mal, suspicious=sus, harmless=har, undetected=und,
        )

    def _parse_file_result(self, file_name: str, raw: dict) -> ScanResult:
        try:
            mal, sus, har, und = self._stats_from(raw["data"]["attributes"])
        except Exception:
            return ScanResult(item_type=ItemType.FILE, value=file_name,
                              verdict=ScanVerdict.UNKNOWN)
        return ScanResult(
            item_type=ItemType.FILE, value=file_name, verdict=_classify(mal, sus),
            malicious=mal, suspicious=sus, harmless=har, undetected=und,
        )
