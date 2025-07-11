from rapidfuzz import fuzz
import re
import regex
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
    stripped = re.sub(r"\s+", "", text.strip())
    if not stripped:
        return False

    # Match emoji characters
    emoji_char = regex.compile(r"\p{Emoji}", flags=regex.UNICODE)
    
    return all(emoji_char.fullmatch(char) for char in stripped)
