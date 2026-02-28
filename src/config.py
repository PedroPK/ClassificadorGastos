from __future__ import annotations

from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "categories.yaml"


def _load() -> tuple[dict[str, list[str]], str]:
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data.get("categories", {}), data.get("default_category", "Outros")


CATEGORY_RULES, DEFAULT_CATEGORY = _load()
