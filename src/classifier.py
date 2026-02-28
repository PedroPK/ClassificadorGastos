from __future__ import annotations

from src.config import CATEGORY_RULES, DEFAULT_CATEGORY


def classify_description(description: str) -> str:
    text = description.lower().strip()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return DEFAULT_CATEGORY
