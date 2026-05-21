from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BotStats:
    total_users: int
    today_users: int
    total_scans: int
    dangerous: int
    suspicious: int
    bl_count: int
