import re
from datetime import datetime


def to_datetime(text: str) -> datetime:
    match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)
    raise ValueError(f"Invalid date format: {text}")
