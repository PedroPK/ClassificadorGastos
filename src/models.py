from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    date: datetime
    description: str
    amount: float
    source_file: str
    source_type: str
