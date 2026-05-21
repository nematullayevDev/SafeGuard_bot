from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Warning:
    chat_id: int
    user_id: int
    reason: str
    warned_at: str
