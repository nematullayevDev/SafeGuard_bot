import logging
import re
from typing import Optional

from app.models import HistoryEntry, ItemType, ScanResult, ScanVerdict
from app.repositories import BlacklistRepository, HistoryRepository
from app.services.virustotal_service import VirusTotalService

logger = logging.getLogger(__name__)


# Regular expressions for bot handles and links
BOT_MENTION_RE = re.compile(r'@([a-zA-Z0-9_]{4,}bot)\b', re.IGNORECASE)
BOT_LINK_RE = re.compile(r'(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/([a-zA-Z0-9_]{4,}bot)\b', re.IGNORECASE)

OFFICIAL_SAFE_HANDLES = {
    # Click
    "clickuz", "clickuzbot", "click_premium_bot", "clickuz_bot", "clickuz_support_bot",
    # Payme
    "payme_uz", "paymeuzbot", "payme_support_bot", "payme",
    # Anorbank
    "anorbank", "anorbankbot", "anorbank_bot", "anorbankuz",
    # NBU / Milliy
    "nbu_official", "milliy_nbu", "nbu_bot", "milliy_bot", "nbuofficial", "nationalbankuz",
    # Kapitalbank
    "kapitalbank", "kapital24", "kapitalbankbot", "kapital365_bot", "kapitalbankuz",
    # Hamkorbank
    "hamkorbankuz", "hamkorbankbot", "hamkorbank_bot", "hamkorbank",
    # SQB (O'zsanoatqurilishbank)
    "sqbuz", "sqb_bot", "sqb_assistant_bot", "sqb", "sqb_official_bot",
    # Agrobank
    "agrobankuz", "agrobankuzbot", "agrobank_bot", "agrobank",
    # Xalq banki
    "xalqbankuz", "xalqbankuzbot", "xalqbank_bot", "xalqbank",
    # Uzcard
    "uzcard_uz", "uzcard_bot", "uzcard",
    # Humo
    "humocard", "humocard_bot", "humo",
    # TBC Bank
    "tbcbankuz", "tbcbankuzbot", "tbcbank",
    # Ipak Yo'li Banki
    "ipakyulibankuz", "ipakyulibank_bot", "ipakyulibank", "ipak_yuli_bank",
    # Aloqabank
    "aloqabankuz", "aloqabank_bot", "aloqabank",
    # Mikrokreditbank (MKBank)
    "mkbuz", "mkb_bot", "mikrokreditbankuz", "mkbank",
    # Infinbank
    "infinbankuz", "infinbank_bot", "infinbank",
    # Davrbank
    "davrbankuz", "davrbankbot", "davr_bank",
    # Turonbank
    "turonbankuz", "turonbank_bot", "turonbank",
    # KDB Bank Uzbekistan
    "kdbuzbekistan", "kdbuzbekistan_bot", "kdb",
    # Ziraat Bank
    "ziraatbankuz", "ziraatbankuz_bot", "ziraatbank",
    # Paynet
    "paynetuz", "paynetuz_bot", "paynet",
    # Paygo
    "paygouz", "paygouz_bot", "paygo",
    # Upay
    "upayuz", "upayuz_bot", "upay",
    # Uzum (Uzum Bank, Uzum Market, Uzum Pay)
    "uzumbank", "uzumbank_bot", "uzumpay", "uzumpay_bot", "uzum_market", "uzum", "uzum_pay",
    # Oson
    "osonuz", "osonuz_bot", "oson",
    # Apelsin
    "apelsin_uz", "apelsinuz_bot", "apelsin",
    # Madad
    "madad_bot", "madaduz",
    # Government/Official
    "soliq_uz", "soliquzbot", "egovuz", "mygovuz", "mygovuz_bot", "davxizmat", "davxizmatbot",
    "pensionjambot", "pfuzbot", "mvd_uz", "mvd_uz_bot", "yolpatruli_bot", "dyhxb_bot"
}

PHISHING_KEYWORDS = [
    # Financial keywords
    "bank", "bnk", "click", "payme", "pay", "card", "humo", "uzcard", "anor", "nbu", "milliy", 
    "kapital", "agro", "xalq", "tbc", "hamkor", "sqb", "uzum", "oson", "paynet", "upay", 
    "apelsin", "davr", "infin", "aloqa", "savdo",
    # Bait keywords
    "mukofot", "yutuq", "aksiy", "aksiya", "sovg", "priz", "fond"
]


def check_phishing_bot(value: str) -> Optional[ScanResult]:
    """
    Checks if a URL or text is a Telegram bot and flags it if it's a suspicious phishing bot.
    Returns ScanResult if it is a bot (either Safe or Dangerous), otherwise None.
    """
    username = None
    
    # Check if value is a mention (e.g. @Armnbnk9542_bot)
    mention_match = BOT_MENTION_RE.search(value)
    if mention_match:
        username = mention_match.group(1)
    else:
        # Check if value is a link (e.g. t.me/Armnbnk9542_bot)
        link_match = BOT_LINK_RE.search(value)
        if link_match:
            username = link_match.group(1)
            
    if not username:
        return None
        
    username_lower = username.lower()
    
    # 2. Check if username is in the whitelist of official safe handles
    if username_lower in OFFICIAL_SAFE_HANDLES:
        return ScanResult(
            item_type=ItemType.LINK,
            value=value,
            verdict=ScanVerdict.SAFE,
            harmless=70,
            description="Ushbu Telegram boti rasmiy va tasdiqlangan tashkilotga tegishli (Xavfsiz)."
        )
        
    # Simplify username: remove non-alphabetic characters for keyword checking
    simplified = re.sub(r'[^a-z]', '', username_lower)
    
    # 3. Check if simplified username contains any phishing/financial keywords
    matched_keyword = None
    for kw in PHISHING_KEYWORDS:
        if kw in simplified:
            matched_keyword = kw
            break
            
    if matched_keyword:
        return ScanResult(
            item_type=ItemType.LINK,
            value=value,
            verdict=ScanVerdict.DANGEROUS,
            malicious=70,
            description=(
                f"🚨 <b>FISHING BOTI ANIQLANDI!</b>\n\n"
                f"Ushbu bot rasmiy bank yoki to'lov tizimiga tegishli emas, lekin nomida ularga "
                f"o'xshash belgilarni ishlatadi (aniqlangan kalit: <i>'{matched_keyword}'</i>).\n"
                f"⚠️ <b>DIQQAT:</b> Bu bot orqali plastik kartangiz ma'lumotlarini yoki SMS kodlarini kiritmang!"
            )
        )
        
    # If it's a bot but doesn't mimic any banking/bait keyword, we return SAFE
    return ScanResult(
        item_type=ItemType.LINK,
        value=value,
        verdict=ScanVerdict.SAFE,
        harmless=70,
        description="Ushbu botda hozircha hech qanday shubhali kiber-tahdid belgilari aniqlanmadi."
    )


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
            # 1. Run phishing bot checks first
            phish_result = check_phishing_bot(url)
            if phish_result:
                result = phish_result
            else:
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
