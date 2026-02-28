from __future__ import annotations

import streamlit as st

from config import CONFIG_PATH, load_categories


@st.cache_data
def _cached_categories(mtime: float) -> tuple[dict[str, list[str]], str]:
    """Recarrega as categorias do YAML sempre que o arquivo for salvo."""
    return load_categories()


def classify_description(description: str) -> str:
    mtime = CONFIG_PATH.stat().st_mtime
    category_rules, default_category = _cached_categories(mtime)
    text = description.lower().strip()
    for category, keywords in category_rules.items():
        if any(str(keyword).lower() in text for keyword in keywords):
            return category
    return default_category
