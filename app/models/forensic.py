from dataclasses import dataclass


@dataclass(frozen=True)
class ForensicCase:
    id: int
    chat_id: int
    chat_title: str
    user_id: int
    full_name: str
    username: str
    phone: str
    message_text: str
    violation_type: str
    reason: str
    detected_at: str
    photo_path: str | None = None

    @property
    def display_violation(self) -> str:
        return {
            "extremism": "Diniy ekstremizm va radikalizm",
            "drugs": "Giyohvand moddalar savdosi targ'iboti",
            "bullying": "Kiberbulling va haqorat",
            "link": "Xavfli havola (link)",
            "file": "Xavfli fayl/virus",
        }.get(self.violation_type, "Siyosat buzilishi")
