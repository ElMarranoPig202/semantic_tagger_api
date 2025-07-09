# core/utils.py

from rapidfuzz import fuzz
import re

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
