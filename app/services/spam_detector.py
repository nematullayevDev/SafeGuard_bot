"""Keyword-based spam detection with character normalization."""
import re
from typing import Iterable
from app.services.uzbek_nlp import transliterate_cyr_to_lat


class SpamDetector:
    def __init__(self, keywords: Iterable[str]) -> None:
        self._keywords = tuple(k.lower() for k in keywords)

    def is_spam(self, text: str) -> bool:
        if not text:
            return False
        
        # 1. Transliterate to Latin if Cyrillic characters are detected
        # (Spammers often mix Cyrillic and Latin to bypass filters)
        t = text.lower()
        has_cyrillic = bool(re.search('[а-яА-ЯёЁўЎқҚғҒҳҲ]', t))
        if has_cyrillic:
            t = transliterate_cyr_to_lat(t)
            t = t.lower()
            
        # 2. Standardize apostrophes
        t = re.sub(r"[‘`ʻ’]", "'", t)
        
        # 3. Check for keywords
        return any(k in t for k in self._keywords)
