from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from src.models import Transaction


def _normalize_amount(value: object) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    raw = str(value).strip().replace("R$", "").replace(" ", "")
    if not raw:
        return None

    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except ValueError:
        return None


def _find_col(columns: list[str], candidates: list[str]) -> Optional[str]:
    lowered = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        for col_lower, col_raw in lowered.items():
            if candidate in col_lower:
                return col_raw
    return None


def parse_csv(file_path: Path) -> list[Transaction]:
    dataframe = pd.read_csv(file_path, sep=None, engine="python")

    date_col = _find_col(dataframe.columns.tolist(), ["data", "date", "lancamento", "lançamento"])
    desc_col = _find_col(dataframe.columns.tolist(), ["descricao", "descrição", "historico", "histórico", "memo"])
    amount_col = _find_col(dataframe.columns.tolist(), ["valor", "amount", "total"])
    debit_col = _find_col(dataframe.columns.tolist(), ["debit", "debito", "débito"])
    credit_col = _find_col(dataframe.columns.tolist(), ["credit", "credito", "crédito"])

    if not date_col or not desc_col or (not amount_col and not debit_col and not credit_col):
        return []

    transactions: list[Transaction] = []

    for _, row in dataframe.iterrows():
        date_value = pd.to_datetime(row[date_col], errors="coerce", dayfirst=True)
        if pd.isna(date_value):
            continue

        if amount_col:
            amount = _normalize_amount(row.get(amount_col))
        else:
            debit = _normalize_amount(row.get(debit_col)) if debit_col else 0.0
            credit = _normalize_amount(row.get(credit_col)) if credit_col else 0.0
            amount = (debit or 0.0) - (credit or 0.0)

        if amount is None:
            continue

        transactions.append(
            Transaction(
                date=date_value.to_pydatetime(),
                description=str(row[desc_col]).strip(),
                amount=float(amount),
                source_file=file_path.name,
                source_type="csv",
            )
        )

    return transactions
