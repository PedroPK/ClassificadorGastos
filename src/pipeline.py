from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable
from zipfile import BadZipFile, ZipFile

import pandas as pd

from classifier import classify_description, should_ignore
from parsers.csv_parser import parse_csv
from parsers.ofx_parser import parse_ofx
from parsers.pdf_parser import parse_pdf

SUPPORTED_EXTENSIONS = {".csv", ".ofx", ".pdf"}
FORMAT_BASE_SCORE = {
    "ofx": 30,
    "csv": 20,
    "pdf": 10,
}


def _parse_file(file_path: Path, source_file_override: str | None = None):
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        items = parse_csv(file_path)
    elif suffix == ".ofx":
        items = parse_ofx(file_path)
    elif suffix == ".pdf":
        items = parse_pdf(file_path)
    else:
        items = []

    if source_file_override:
        for item in items:
            item.source_file = source_file_override
    return items


def _zip_supported_files(zip_path: Path, temp_root: Path, zip_index: int) -> Iterable[tuple[Path, str]]:
    zip_extract_folder = temp_root / f"zip_{zip_index}_{zip_path.stem}"
    zip_extract_folder.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "r") as archive:
        archive.extractall(zip_extract_folder)

    for internal_file in sorted(zip_extract_folder.rglob("*")):
        if not internal_file.is_file():
            continue
        if internal_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        relative = internal_file.relative_to(zip_extract_folder).as_posix()
        source_label = f"{zip_path.name}!{relative}"
        yield internal_file, source_label


def _select_best_source_per_month(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    df = dataframe.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["_desc_len"] = df["description"].astype(str).str.strip().str.len()

    grouped = (
        df.groupby(["month", "source_type"], as_index=False)
        .agg(
            tx_count=("amount", "size"),
            unique_desc=("description", "nunique"),
            avg_desc_len=("_desc_len", "mean"),
        )
    )

    grouped["format_base"] = grouped["source_type"].map(FORMAT_BASE_SCORE).fillna(0)
    grouped["quality_score"] = (
        grouped["tx_count"] * 100
        + grouped["unique_desc"] * 5
        + grouped["avg_desc_len"]
        + grouped["format_base"]
    )

    best = (
        grouped.sort_values(["month", "quality_score"], ascending=[True, False])
        .drop_duplicates(subset=["month"], keep="first")
        [["month", "source_type"]]
        .rename(columns={"source_type": "selected_source_type"})
    )

    selected = df.merge(best, on="month", how="left")
    selected = selected.loc[selected["source_type"] == selected["selected_source_type"]].copy()
    return selected.drop(columns=["selected_source_type", "_desc_len"])


def _drop_cross_file_duplicates(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    df = dataframe.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["_desc_key"] = df["description"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    df["_amount_key"] = df["amount"].round(2)

    duplicated_mask = df.duplicated(subset=["month", "date", "_desc_key", "_amount_key"], keep="first")
    deduplicated = df.loc[~duplicated_mask].copy()
    return deduplicated.drop(columns=["_desc_key", "_amount_key"])


def load_transactions(input_dir: str = "Input") -> pd.DataFrame:
    folder = Path(input_dir)
    if not folder.exists():
        return pd.DataFrame(columns=["date", "description", "amount", "source_file", "source_type", "category"])

    all_items = []
    with TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)

        for zip_index, file_path in enumerate(sorted(folder.glob("*"))):
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()
            if suffix in SUPPORTED_EXTENSIONS:
                all_items.extend(_parse_file(file_path))
                continue

            if suffix != ".zip":
                continue

            try:
                for internal_file, source_label in _zip_supported_files(file_path, temp_root, zip_index):
                    all_items.extend(_parse_file(internal_file, source_label))
            except BadZipFile:
                continue

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
    dataframe = dataframe[~dataframe["description"].map(should_ignore)].copy()
    dataframe = _select_best_source_per_month(dataframe)
    dataframe = _drop_cross_file_duplicates(dataframe)
    dataframe["category"] = dataframe["description"].astype(str).map(classify_description)
    dataframe = dataframe.sort_values("date").reset_index(drop=True)
    dataframe = dataframe.drop(columns=["month"], errors="ignore")
    return dataframe
