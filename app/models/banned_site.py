from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BannedSite:
    id: int
    platform: str
    name: str
    added_at: str
    is_new: bool
