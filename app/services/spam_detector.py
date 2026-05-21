"""Keyword-based spam detection."""
from typing import Iterable


class SpamDetector:
    def __init__(self, keywords: Iterable[str]) -> None:
        self._keywords = tuple(k.lower() for k in keywords)

    def is_spam(self, text: str) -> bool:
        if not text:
            return False
        t = text.lower()
        return any(k in t for k in self._keywords)
