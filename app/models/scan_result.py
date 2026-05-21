from dataclasses import dataclass

from app.models.enums import ItemType, ScanVerdict


@dataclass(frozen=True, slots=True)
class ScanResult:
    item_type: ItemType
    value: str           # URL or file name
    verdict: ScanVerdict
    malicious: int = 0
    suspicious: int = 0
    harmless: int = 0
    undetected: int = 0
    error: str = ""

    @property
    def total_engines(self) -> int:
        return self.malicious + self.suspicious + self.harmless + self.undetected


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    item_type: ItemType
    value: str
    verdict: ScanVerdict
    scanned_at: str
