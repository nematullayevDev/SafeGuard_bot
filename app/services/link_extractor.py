"""Extract URLs from aiogram messages (entities + plain text)."""
from aiogram.types import Message


def extract_links(message: Message) -> list[str]:
    links: list[str] = []
    entities = message.entities or message.caption_entities or []
    text = message.text or message.caption or ""

    for e in entities:
        if e.type == "url":
            links.append(text[e.offset:e.offset + e.length])
        elif e.type == "text_link" and e.url:
            links.append(e.url)
        elif e.type == "mention":
            mention_text = text[e.offset:e.offset + e.length]
            if mention_text.lower().endswith("bot"):
                username = mention_text.lstrip("@")
                links.append(f"https://t.me/{username}")

    for word in text.split():
        if word.startswith(("http://", "https://")) and word not in links:
            links.append(word)
        elif word.startswith("@") and word.lower().endswith("bot"):
            username = word.lstrip("@").rstrip(".,!?()[]{}")
            bot_link = f"https://t.me/{username}"
            if bot_link not in links:
                links.append(bot_link)

    return links
