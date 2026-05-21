from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Group:
    chat_id: int
    title: str
    username: str
    is_active: bool
    added_at: str

    @property
    def at_username(self) -> str:
        return f"@{self.username}" if self.username else "—"

    @property
    def display_title(self) -> str:
        return self.title or "Noma'lum"
