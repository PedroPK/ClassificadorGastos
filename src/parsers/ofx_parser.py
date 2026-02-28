from __future__ import annotations

from pathlib import Path

from ofxparse import OfxParser

from models import Transaction


def parse_ofx(file_path: Path) -> list[Transaction]:
    with file_path.open("rb") as fp:
        ofx = OfxParser.parse(fp)

    transactions: list[Transaction] = []
    accounts = ofx.account.statement.transactions if ofx.account else []

    for item in accounts:
        description = item.memo or item.payee or "Sem descrição"
        transactions.append(
            Transaction(
                date=item.date,
                description=description.strip(),
                amount=float(item.amount),
                source_file=file_path.name,
                source_type="ofx",
            )
        )

    return transactions
