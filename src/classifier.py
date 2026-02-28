from __future__ import annotations

import streamlit as st

from config import CONFIG_PATH, load_categories


@st.cache_data
def _cached_categories(mtime: float) -> tuple[dict[str, list[str]], str, list[str]]:
    """Recarrega as categorias do YAML sempre que o arquivo for salvo."""
    return load_categories()


def _get_cached(mtime: float) -> tuple[dict[str, list[str]], str, list[str]]:
    return _cached_categories(mtime)


def should_ignore(description: str) -> bool:
    mtime = CONFIG_PATH.stat().st_mtime
    _, _, ignore_patterns = _get_cached(mtime)
    text = description.lower().strip()
    return any(pattern in text for pattern in ignore_patterns)


def classify_description(description: str) -> str:
    mtime = CONFIG_PATH.stat().st_mtime
    category_rules, default_category, _ = _get_cached(mtime)
    text = description.lower().strip()
    for category, keywords in category_rules.items():
        if any(str(keyword).lower() in text for keyword in keywords):
            return category
    return default_category
