from rapidfuzz import fuzz
import re
import emoji

def is_similar(a: str, b: str, threshold: int = 80) -> bool:
    return fuzz.token_sort_ratio(a, b) > threshold

def deduplicate_topics(topics: list[str]) -> list[str]:
    result: list[str] = []
    for t in topics:
        if not any(is_similar(t, existing) for existing in result):
            result.append(t)
    return result

def strip_apologies(text: str) -> str:
    lines = text.splitlines()
    filtered = [
        l for l in lines
        if not re.search(
            r"\b(i apologize|sorry|as an ai|i am unable|i cannot)\b",
            l.lower()
        )
    ]
    return "\n".join(filtered)
# core/utils.py  (append below existing code)

META_KEYWORDS = [
    "json", "escape", "escaping", "emoticon", "array", "example"
]

def filter_meta_topics(topics: list[str]) -> list[str]:
    cleaned = []
    for t in topics:
        low = t.lower()
        if not any(kw in low for kw in META_KEYWORDS):
            cleaned.append(t)
    return cleaned



def is_emoji_only(text: str) -> bool:
    # Remove spaces, invisible characters
    stripped = re.sub(r"\s+", "", text.strip())

    # Emoji regex (Unicode blocks)
    emoji_pattern = re.compile(
        r"^(?:[\u2600-\u27BF\u1F300-\u1F6FF\u1F900-\u1F9FF\u1FA70-\u1FAFF\u1F680-\u1F6FF\u1F600-\u1F64F"
        r"\u200D\uFE0F\u23CF\u23E9-\u23FA\u24C2\u25AA-\u25FE\u00A9\u00AE\u3030\u2B05-\u2B07\u2934\u2935"
        r"\u2190-\u21FF]+)+$"
    )

    return bool(emoji_pattern.match(stripped))