from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.classifier import classify_description
from src.parsers.csv_parser import parse_csv
from src.parsers.ofx_parser import parse_ofx
from src.parsers.pdf_parser import parse_pdf


def _parse_file(file_path: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return parse_csv(file_path)
    if suffix == ".ofx":
        return parse_ofx(file_path)
    if suffix == ".pdf":
        return parse_pdf(file_path)
    return []


def load_transactions(input_dir: str = "Input") -> pd.DataFrame:
    folder = Path(input_dir)
    if not folder.exists():
        return pd.DataFrame(columns=["date", "description", "amount", "source_file", "source_type", "category"])

    all_items = []
    for file_path in sorted(folder.glob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".csv", ".ofx", ".pdf"}:
            continue
        all_items.extend(_parse_file(file_path))

    if not all_items:
        return pd.DataFrame(columns=["date", "description", "amount", "source_file", "source_type", "category"])

    dataframe = pd.DataFrame(
        [
            {
                "date": item.date,
                "description": item.description,
                "amount": item.amount,
                "source_file": item.source_file,
                "source_type": item.source_type,
            }
            for item in all_items
        ]
    )
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    dataframe = dataframe.dropna(subset=["date", "description", "amount"])
    dataframe["category"] = dataframe["description"].astype(str).map(classify_description)
    dataframe = dataframe.sort_values("date").reset_index(drop=True)
    return dataframe
