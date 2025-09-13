from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from selenium.webdriver.remote.webelement import WebElement

from database import T_LotteryEntryRecord
from typing import Optional


@dataclass
class LotteryEntry:
    date: datetime
    start: int
    end: int
    value: str
    amount: int
    link: Optional[WebElement]
    row: Optional[WebElement]
    account_group: Optional[str] = None

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("開始時間は終了時間より前である必要があります")
        if self.amount >= 1:
            raise ValueError("コート面数は1以上である必要があります")
        if not self.value.strip():
            raise ValueError("コートValueは空にできません")

    def core(self) -> LotteryEntry:
        return replace(self, link=None, row=None)

    def to_record(self) -> T_LotteryEntryRecord:
        if not self.account_group:
            raise ValueError("アカウントグループは必須です")
        return T_LotteryEntryRecord(
            date=self.date,
            start=self.start,
            end=self.end,
            value=self.value,
            amount=self.amount,
            account_group=self.account_group,
        )

    def key(self) -> tuple:
        return (
            self.date,
            self.start,
            self.end,
            self.value,
            self.amount,
        )

    def duration_minutes(self) -> int:
        """予約時間の長さを分で返す"""
        return self.end - self.start

    def __eq__(self, other) -> bool:
        if not isinstance(other, LotteryEntry):
            return False
        return self.key() == other.key()
