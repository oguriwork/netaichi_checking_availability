from dataclasses import dataclass
from typing import Optional


@dataclass
class CourtInfo:
    name: str
    value: str
    applications: int
    MAX_APPLICATIONS: int = 30

    @property
    def remaining(self) -> int:
        return self.MAX_APPLICATIONS - self.applications



@dataclass
class SummaryInfo:
    alltime: int = 0
    zone: int = 0
    count: int = 0

class LotteryStatus:
    def __init__(self, court_infos: list[CourtInfo], summary: SummaryInfo):
        self.court_infos = court_infos
        self.summary = summary

    def get_by_name(self, name: str) -> Optional[CourtInfo]:
        return next((ci for ci in self.court_infos if ci.name == name), None)

    def get_by_value(self, value: str | int) -> Optional[CourtInfo]:
        return next(
            (ci for ci in self.court_infos if str(ci.value) == str(value)), None
        )

    def full_courts(self) -> list[CourtInfo]:
        return [ci for ci in self.court_infos if ci.applications >= ci.MAX_APPLICATIONS]

    def available_courts(self) -> list[CourtInfo]:
        return [ci for ci in self.court_infos if ci.applications < ci.MAX_APPLICATIONS]
