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
    'Ў': "o'", 'ў': "o'",
    'Қ': 'q', 'қ': 'q',
    'Ғ': "g'", 'ғ': "g'",
    'Ҳ': 'h', 'ҳ': 'h'
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


def stem_uzbek_word(word: str) -> str:
    """Strips common Uzbek suffixes iteratively to find the root."""
    w = word.strip().lower()
    if len(w) < 4:
        return w

    # Suffixes in decreasing order of length to avoid partial matches
    suffixes = [
        # Continuous aspect & complex verb endings
        "moqdamiz", "moqdasiz", "moqdalar", "moqdaman", "moqdasan", "moqda",
        "yaptilar", "yapsiz", "yapmiz", "yapman", "yapsan", "yapti",
        "ganman", "gansan", "ganmiz", "gansiz", "ganlar", "gan",
        "diganman", "digansan", "diganmiz", "digansiz", "diganlar", "digan",
        # Standard verb endings
        "adilar", "asiz", "amiz", "aman", "asan", "adi",
        "aydilar", "aysiz", "aymiz", "ayman", "aysan", "aydi",
        "dingiz", "dilar", "dim", "ding", "dik", "di",
        "salar", "sam", "sang", "sak", "sangiz", "sa",
        # Plural and complex case forms
        "dagilar", "dagi", "larimiz", "laringiz", "lari", "lar",
        # Noun/adjective derivation suffixes
        "chilik", "chilar", "likda", "likdan", "liklar", "lik", "chi",
        "vchilar", "vchi", "uvchilar", "uvchi", "moq", "ish", "ishlar",
        # Case endings
        "ning", "dan", "ga", "ka", "qa", "da", "ni",
        # Possessives
        "imiz", "ingiz", "ing", "im", "i", "si",
        # Particles
        "mi", "dir", "ku", "u", "da"
    ]

    changed = True
    while changed:
        changed = False
        for suffix in suffixes:
            if w.endswith(suffix):
                # Ensure root doesn't become too short (min 3 chars)
                if len(w) - len(suffix) >= 3:
                    w = w[:-len(suffix)]
                    changed = True
                    break
    return w


def simplify_word(word: str) -> str:
    """
    Simplifies spelling variations and normalizes leet-speak/repeats:
    - Replaces common leet-speak characters (e.g. @->a, 0->o).
    - Collapses consecutive repeated characters.
    - Lowers case, normalizes O'/G' apostrophes, and replaces x->h.
    - Strips non-alphanumeric symbols.
    """
    w = word.lower()
    w = re.sub(r"[‘`ʻ’']", "", w)
    w = normalize_leet(w)
    w = collapse_repeats(w)
    w = w.replace("x", "h")
    w = re.sub(r"[^a-z0-9]", "", w)
    return w


def simplify_text_preserve_spaces(text: str) -> str:
    """Simplifies text for phrase matching while preserving spaces."""
    w = text.lower()
    w = w.replace("-", " ")
    w = re.sub(r"[‘`ʻ’']", "", w)
    w = normalize_leet(w)
    w = collapse_repeats(w)
    w = w.replace("x", "h")
    # Preserve alphanumeric, spaces, and leet characters
    w = re.sub(r"[^a-z0-9\s]", "", w)
    w = re.sub(r"\s+", " ", w)
    return w.strip()


def collapse_repeats(word: str) -> str:
    """Collapses consecutive repeated characters to a single character (e.g., 'dabbba' -> 'daba')."""
    if not word:
        return ""
    result = [word[0]]
    for char in word[1:]:
        if char != result[-1]:
            result.append(char)
    return "".join(result)


LEET_MAP = {
    '0': 'o', '1': 'i', '!': 'i', '@': 'a', '4': 'a', '3': 'e', '$': 's', '7': 't', '8': 'b'
}


def normalize_leet(word: str) -> str:
    """Replaces common leet-speak character substitutions with standard letters."""
    return "".join(LEET_MAP.get(c, c) for c in word.lower())


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]


def is_fuzzy_match(word: str, keyword: str) -> bool:
    """
    Determines if a word fuzzy-matches a keyword under Uzbek moderation rules:
    - Normalizes leet-speak and collapses repeated characters.
    - If keyword is short (< 5 chars), requires exact match.
    - If keyword is 5 or 6 chars, allows 1 edit (Levenshtein distance <= 1).
    - If keyword is >= 7 chars, allows up to 2 edits (Levenshtein distance <= 2).
    - Also performs substring matching for keywords >= 4 chars.
    """
    w = collapse_repeats(normalize_leet(word))
    kw = collapse_repeats(normalize_leet(keyword))
    
    if w == kw:
        return True
        
    if len(kw) >= 4 and kw in w:
        return True
        
    n = len(kw)
    if n < 5:
        return False
        
    dist = levenshtein_distance(w, kw)
    if n >= 7:
        return dist <= 2
    else:  # n is 5 or 6
        return dist <= 1


class UzbekNLPService:
    def __init__(self, gemini_api_key: Optional[str] = None) -> None:
        self._api_key = gemini_api_key
        
        # High-fidelity keyword lists
        self._extremism_keywords = {
            "jihod", "hijrat", "xalifa", "xalifalik", "hizb ut-tahrir", "akromiy", 
            "akromiylar", "akramiya", "salaf", "salafiylar", "salafiy", "vahobiy", 
            "vahobiylar", "islomiy davlat", "isid", "daish", "shariat", "tovhid", 
            "tavhid", "kufr", "murtad", "kofir", "mushrik", "jihodchi", "muhojir", 
            "ansor", "ansoriy", "qitol", "g'azot", "g'azovat", "shahid", "shohid", 
            "katiba", "jundulloh", "tahrirchi", "islom nuri", "tavxid", "halifalik"
        }
        
        self._drugs_keywords = {
            "soli", "soli dori", "mefedron", "mef", "kristall", "geroin", "ko'knor", "konoplya", 
            "tramadol", "lyrika", "lrika", "lira", "skorost", "spays", "doperun", 
            "kladmen", "klad", "kurir", "kuryer", "zakladka", "anasha", "gash", 
            "gashish", "tropicamid", "tropikamid", "sintetika", "giyohvand", 
            "psixotrop", "baku", "reglan", "optom sol", "narkotik", "koks", 
            "kokain", "nasha", "nasha urug'i", "atxod", "preparat", "giyoh", 
            "shirinlik", "kristal"
        }
        
        self._bullying_keywords = {
            "suka", "jalap", "blat", "am", "qo'tag'", "qotoq", "qanciq", "yaramas", 
            "iflos", "o'ldir", "so'yaman", "sharmanda", "gandon", "kot", "pidar", 
            "dalbayob", "axmoq", "xarom", "harom", "yebsan", "sik", "sikaman", 
            "koting", "jallod", "chort", "tvar", "gandonlar", "kallangni", 
            "tahdid", "zo'rlayman", "ursang", "o'ldiraman", "yuzingni yirtaman", 
            "sharmandangni chiqaraman", "gejga solaman", "urib o'ldiraman","skaman","seks","siks","sex"
        }

    def normalize_text(self, text: str) -> str:
        """Cleans, normalizes, and transliterates Uzbek text to unified Latin script."""
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
        """Performs advanced local rule-based stemming and spelling variation matching."""
        normalized = self.normalize_text(text)
        
        # Clean text but preserve common leet symbols so they are tokenized as part of words
        clean_text = re.sub(r"[.,?/\\()\[\]{}:;\-_+=*&^%#\"~`]", " ", normalized)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        # Tokenize and stem each word
        raw_words = clean_text.split()
        stemmed_words = [stem_uzbek_word(w) for w in raw_words]
        simplified_stemmed_words = [simplify_word(w) for w in stemmed_words]
        
        # 1. Extremism Check
        for keyword in self._extremism_keywords:
            if " " in keyword:
                simplified_kw_phrase = simplify_text_preserve_spaces(keyword)
                simplified_text_phrase = simplify_text_preserve_spaces(text)
                if simplified_kw_phrase in simplified_text_phrase:
                    return True, "extremism", f"Diniy ekstremistik yoki radikal g'oyalar targ'iboti aniqlandi (Tahlil: '{keyword}')"
            else:
                simplified_kw = simplify_word(keyword)
                for idx, w in enumerate(simplified_stemmed_words):
                    if is_fuzzy_match(w, simplified_kw):
                        original_match = raw_words[idx]
                        return True, "extremism", f"Diniy ekstremistik yoki radikal g'oyalar targ'iboti aniqlandi (Kalit so'z: '{original_match}')"

        # 2. Drugs Check
        for keyword in self._drugs_keywords:
            if " " in keyword:
                simplified_kw_phrase = simplify_text_preserve_spaces(keyword)
                simplified_text_phrase = simplify_text_preserve_spaces(text)
                if simplified_kw_phrase in simplified_text_phrase:
                    return True, "drugs", f"Giyohvand moddalar yashirin savdosi yoki targ'iboti aniqlandi (Tahlil: '{keyword}')"
            else:
                simplified_kw = simplify_word(keyword)
                for idx, w in enumerate(simplified_stemmed_words):
                    if is_fuzzy_match(w, simplified_kw):
                        original_match = raw_words[idx]
                        return True, "drugs", f"Giyohvand moddalar yashirin savdosi yoki targ'iboti aniqlandi (Jargon: '{original_match}')"

        # 3. Cyberbullying Check
        for keyword in self._bullying_keywords:
            if " " in keyword:
                simplified_kw_phrase = simplify_text_preserve_spaces(keyword)
                simplified_text_phrase = simplify_text_preserve_spaces(text)
                if simplified_kw_phrase in simplified_text_phrase:
                    return True, "bullying", f"Kiberbulling, tahdid yoki haqorat elementlari aniqlandi (Tahlil: '{keyword}')"
            else:
                simplified_kw = simplify_word(keyword)
                for idx, w in enumerate(simplified_stemmed_words):
                    if is_fuzzy_match(w, simplified_kw):
                        original_match = raw_words[idx]
                        return True, "bullying", f"Kiberbulling, tahdid yoki og'ir haqorat elementlari aniqlandi (So'z: '{original_match}')"

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
                    "Siz SafeGuard kiber-xavfsizlik tahlilchisisiz. "
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
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=8)) as response:
                        if response.status == 200:
                            data = await response.json()
                            content_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            
                            # Strip markdown code block notation if present
                            if content_text.startswith("```"):
                                content_text = re.sub(r"^```(?:json)?\s*", "", content_text)
                                content_text = re.sub(r"\s*```$", "", content_text)
                                
                            result = json.loads(content_text.strip())
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
