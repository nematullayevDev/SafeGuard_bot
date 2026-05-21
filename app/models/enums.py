"""Domain enums."""
from enum import Enum


class ScanVerdict(str, Enum):
    SAFE = "xavfsiz"
    SUSPICIOUS = "shubhali"
    DANGEROUS = "xavfli"
    UNKNOWN = "noma'lum"

    @property
    def is_bad(self) -> bool:
        return self in (ScanVerdict.DANGEROUS, ScanVerdict.SUSPICIOUS)


class ItemType(str, Enum):
    LINK = "link"
    FILE = "fayl"
