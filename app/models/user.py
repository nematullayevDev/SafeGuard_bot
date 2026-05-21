from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    user_id: int
    first_name: str
    username: str
    phone: str
    registered_at: str

    @property
    def at_username(self) -> str:
        return f"@{self.username}" if self.username else "Yo'q"

    @property
    def display_name(self) -> str:
        return self.first_name or "Noma'lum"
