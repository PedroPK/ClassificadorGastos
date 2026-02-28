from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pdfplumber

from models import Transaction

LINE_PATTERN = re.compile(
    r"(?P<date>\d{2}/\d{2}(?:/\d{2,4})?)\s+(?P<desc>.+?)\s+(?P<amount>-?\d[\d\.,]*)$"
)


def _parse_date(raw: str) -> datetime | None:
    parts = raw.split("/")
    if len(parts) == 2:
        day, month = parts
        year = datetime.now().year
        raw = f"{day}/{month}/{year}"
    try:
        return datetime.strptime(raw, "%d/%m/%Y")
    except ValueError:
        try:
            return datetime.strptime(raw, "%d/%m/%y")
        except ValueError:
            return None


def _parse_amount(raw: str) -> float | None:
    value = raw.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def parse_pdf(file_path: Path) -> list[Transaction]:
    transactions: list[Transaction] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue

                match = LINE_PATTERN.search(line)
                if not match:
                    continue

                date = _parse_date(match.group("date"))
                amount = _parse_amount(match.group("amount"))
                description = match.group("desc").strip()

                if not date or amount is None:
                    continue

                transactions.append(
                    Transaction(
                        date=date,
                        description=description,
                        amount=amount,
                        source_file=file_path.name,
                        source_type="pdf",
                    )
                )

    return transactions
