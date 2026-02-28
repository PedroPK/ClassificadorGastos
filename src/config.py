from __future__ import annotations

from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "categories.yaml"


def load_categories() -> tuple[dict[str, list[str]], str, list[str]]:
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return (
        data.get("categories", {}),
        data.get("default_category", "Outros"),
        [str(p).lower() for p in data.get("ignore", [])],
    )
