"""Uzbek AI & NLP Moderation Service."""
import json
import logging
import re
from typing import Any, Dict, Optional, Tuple
import aiohttp

logger = logging.getLogger(__name__)

# Uzbek Cyrillic to Latin character mapping for normalization
CYR_TO_LAT_MAP = {
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x',
    'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Ъ': "'", 'ъ': "'",
    'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya',
    'Ў': "O'", 'ў': "o'",
    'Қ': 'Q', 'қ': 'q',
    'Ғ': "G'", 'ғ': "g'",
    'Ҳ': 'H', 'ҳ': 'h'
}

def transliterate_cyr_to_lat(text: str) -> str:
    """Transliterates Uzbek Cyrillic text to Latin script."""
    result = []
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        # Handle 'Е' / 'е' cases at start of words or after vowels
        if char in ('Е', 'е') and (i == 0 or text[i - 1].isspace() or text[i - 1].lower() in 'аеёиоуэюяў'):
            lat_char = 'Ye' if char == 'Е' else 'ye'
            result.append(lat_char)
        else:
            result.append(CYR_TO_LAT_MAP.get(char, char))
        i += 1
    return "".join(result)


class UzbekNLPService:
    def __init__(self, gemini_api_key: Optional[str] = None) -> None:
        self._api_key = gemini_api_key
        
        # Local high-fidelity wordlists (always in lower-case Latin)
        self._extremism_keywords = {
            "jihod", "xalifalik", "hizb ut-tahrir", "hizb ut tahrir", "akromiylar", 
            "soxta dindorlar", "kofirlar", "mushriklar", "hijrat qilish", "jihodchilar", 
            "salafiylar", "vahobiylar", "islomiy davlat", "isid", "shariat qonunlari", 
            "tovhid", "kufr", "murtad", "xalifa", "tahrirchilar", "tahdidiy g'oya",
            "akramiya", "katiba", "tavxid", "halifalik"
        }
        
        self._drugs_keywords = {
            "sol", "mefedron", "mef", "kristall", "geroin", "ko'knor", "konoplya", 
            "tramadol", "lrika", "skorost", "spays", "doperun", "kladmen", "klad", 
            "kurir", "zakladka", "anasha", "gash", "gashish", "tropicamid", "tropikamid", 
            "sintetika", "giyohvand", "psixotrop", "lira", "baku", "reglan", "optom sol"
        }
        
        self._bullying_keywords = {
            "suka", "jalap", "blat", "am", "qo'tag'", "qanciq", "yaramas", "iflos", 
            "o'ldiraman", "so'yaman", "sharmanda", "gandon", "kot", "pidar", "dalbayob", 
            "axmoq", "xarom", "harom", "yebsan", "sik", "sikaman", "qotoq", "koting", 
            "jallod", "chort", "tvar", "gandonlar", "kallangni", "kalla"
        }

    def normalize_text(self, text: str) -> str:
        """Cleans, normalizes, and translates Uzbek text to unified Latin script."""
        if not text:
            return ""
        # 1. Transliterate to Latin if Cyrillic characters are detected
        has_cyrillic = bool(re.search('[а-яА-ЯёЁўЎқҚғҒҳҲ]', text))
        if has_cyrillic:
            text = transliterate_cyr_to_lat(text)
        
        # 2. Lowercase and clean special symbols but preserve apostrophes for O', G'
        text_lower = text.lower()
        # Replace common variations of O' and G' apostrophes with standard single quote
        text_lower = re.sub(r"[‘`ʻ’]", "'", text_lower)
        return text_lower

    def analyze_local(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Performs extremely fast local keyword-based classification."""
        normalized = self.normalize_text(text)
        words = set(re.findall(r"\b\w+(?:'\w+)?\b", normalized))
        
        # 1. Extremism Check
        for keyword in self._extremism_keywords:
            if keyword in normalized:
                # Direct check for phrases, or word-level matches
                if " " in keyword or keyword in words:
                    return True, "extremism", f"Diniy ekstremistik yoki radikal g'oyalar targ'iboti aniqlandi (Kalit so'z: '{keyword}')"
                    
        # 2. Drugs Check
        for keyword in self._drugs_keywords:
            if keyword in normalized:
                if " " in keyword or keyword in words:
                    return True, "drugs", f"Giyohvand moddalar yashirin savdosi yoki targ'iboti aniqlandi (Jargon: '{keyword}')"
                    
        # 3. Cyberbullying Check
        for keyword in self._bullying_keywords:
            if keyword in normalized:
                if " " in keyword or keyword in words:
                    return True, "bullying", f"Kiberbulling, tahdid yoki og'ir haqorat elementlari aniqlandi (So'z: '{keyword}')"
                    
        return False, None, None

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyzes text using Gemini AI model, with local fallback."""
        if not text or len(text.strip()) < 2:
            return {
                "is_violation": False,
                "category": None,
                "reason": "Matn tahlil qilish uchun juda qisqa."
            }

        # If API key is available, use Gemini API
        if self._api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self._api_key}"
                prompt = (
                    "Siz O'zbekiston Respublikasi Ichki Ishlar Vazirligi (IIV) kiber-xavfsizlik tahlilchisisiz. "
                    "Quyidagi matnni tahlil qiling va unda ushbu uchta jinoyat yoki qonunbuzarlik belgilari borligini aniqlang:\n"
                    "- extremism: Oliy sud taqiqlagan radikal diniy g'oyalar, shiorlar, ekstremistik guruhlar (ISID, Hizb ut-Tahrir va b.) targ'iboti.\n"
                    "- drugs: Sintetik giyohvand moddalar (mef, sol, kristall), taqiqlangan dorilar sotilishi, kladmenlik yoki kurirlik yashirin targ'iboti.\n"
                    "- bullying: Guruh ichidagi shaxsga qaratilgan og'ir haqorat, sharmanda qilish yoki o'ldirish/zo'ravonlik tahdidlari.\n\n"
                    f"Tahlil qilinuvchi matn: \"{text}\"\n\n"
                    "Javobni faqat va faqat quyidagi tuzilmaga ega JSON formatida qaytaring, boshqa hech narsa yozmang:\n"
                    "{\n"
                    "  \"is_violation\": true yoki false,\n"
                    "  \"category\": \"extremism\" yoki \"drugs\" yoki \"bullying\" yoki null,\n"
                    "  \"reason\": \"Flagged qilinish sababi yoki xavfsizligi haqida o'zbek tilida tahliliy izoh (maksimal 2 ta gap)\"\n"
                    "}"
                )
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            content_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            result = json.loads(content_text)
                            logger.info("AI NLP tahlil muvaffaqiyatli yakunlandi.")
                            return {
                                "is_violation": bool(result.get("is_violation", False)),
                                "category": result.get("category"),
                                "reason": result.get("reason", "AI tomonidan tahlil qilindi.")
                            }
                        else:
                            logger.warning(f"Gemini API xatosi: status={response.status}. Lokal rejimga o'tiladi.")
            except Exception as e:
                logger.error(f"Gemini API bilan bog'lanishda xatolik: {e}. Lokal rejimga o'tiladi.")

        # Fallback to local high-fidelity rules engine
        is_viol, cat, reason = self.analyze_local(text)
        return {
            "is_violation": is_viol,
            "category": cat,
            "reason": reason or "Matnda hech qanday shubhali qonunbuzarlik belgilari aniqlanmadi (Lokal tahlil)."
        }
