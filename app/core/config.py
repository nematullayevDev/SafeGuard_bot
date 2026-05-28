"""Application configuration loaded from environment variables."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    vt_api_key: str
    admin_id: int
    bot_username: str
    db_path: str
    base_dir: Path
    gemini_api_key: str | None = None

    rate_limit_max: int = 5
    rate_limit_window: int = 60
    max_file_size_mb: int = 32
    max_warnings: int = 3

    spam_keywords: tuple[str, ...] = field(default_factory=lambda: (
        "tabriklaymiz", "yutdingiz", "sovga", "siz tanlandi",
        "maxsus taklif", "bepul pul", "kredit karta", "tezkor daromad",
        "investitsiya", "foiz kafolatli", "hoziroq bosing",
        "prize", "winner", "click here", "free money", "urgent",
        "verify your account", "limited offer", "act now", "claim your",
        "you have been selected", "congratulations you won",
        "bitcoin", "crypto offer", "nft drop", "airdrop", "binance gift",
        "pump signal", "100x guaranteed", "passive income",
        "login required", "account suspended", "unusual activity",
        "confirm your identity", "update your payment",
    ))


def _load() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    vt_api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN .env faylida belgilanmagan!")
    if not vt_api_key:
        raise RuntimeError("VIRUSTOTAL_API_KEY .env faylida belgilanmagan!")

    base = Path(__file__).resolve().parents[2]

    # DB_PATH .env da belgilangan bo'lsa — uni ishlatamiz
    # Aks holda Render.com /var/data disk, yo'q bo'lsa loyiha papkasi
    custom_db = os.getenv("DB_PATH")
    if custom_db:
        db_path = custom_db
    else:
        render_disk = "/var/data"
        if os.path.exists(render_disk) and os.access(render_disk, os.W_OK):
            db_path = os.path.join(render_disk, "users.db")
        else:
            db_path = str(base / "users.db")

    return Settings(
        bot_token=bot_token,
        vt_api_key=vt_api_key,
        admin_id=int(os.getenv("ADMIN_ID", "0")),
        bot_username=os.getenv("BOT_USERNAME", "safeguard_uz_bot"),
        db_path=db_path,
        base_dir=base,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
    )


settings = _load()


PLATFORMS: dict[str, str] = {
    "telegram": "✈️ Telegram",
    "instagram": "📸 Instagram",
    "whatsapp": "💬 WhatsApp",
    "facebook": "👤 Facebook",
    "twitter": "🐦 Twitter/X",
    "youtube": "▶️ YouTube",
    "tiktok": "🎵 TikTok",
}

PLATFORM_NOTES: dict[str, str] = {
    "telegram": "⚠️ O'zbekiston Respublikasi UZINFOCOM tomonidan bloklangan Telegram kanallar va guruhlar.",
    "instagram": "⚠️ Instagram O'zbekistonda rasman taqiqlanmagan, lekin yuqoridagi sahifalar O'zR qonunchiligiga ko'ra man etilgan.",
    "whatsapp": "⚠️ WhatsApp O'zbekistonda rasman taqiqlanmagan. Lekin qonunbuzarlik guruhlari faoliyati jinoyat hisoblanadi.",
    "facebook": "⚠️ Facebook O'zbekistonda qisman cheklangan. Qonunbuzarlik sahifalari UZINFOCOM tomonidan bloklanadi.",
    "twitter": "⚠️ Twitter/X O'zbekistonda vaqti-vaqti bilan cheklanadi. Qonunbuzarlik akkauntlari bloklanadi.",
    "youtube": "⚠️ YouTube O'zbekistonda ishlaydi, lekin yuqoridagi kontent turlari O'zR qonunchiligi bo'yicha taqiqlangan.",
    "tiktok": "⚠️ TikTok O'zbekistonda rasman ishlaydi, lekin davlat nazorati ostida. Qonunbuzarlik kontent bloklanadi.",
}
