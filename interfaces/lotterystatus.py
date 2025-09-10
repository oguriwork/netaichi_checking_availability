from dataclasses import dataclass


@dataclass
class CourtInfo:
    """テニスコート情報を格納するデータクラス"""

    name: str
    value: str
    applications: int
    MAX_APPLICATIONS: int = 30

    @property
    def remaining(self) -> int:
        return self.MAX_APPLICATIONS - self.applications

    def to_dict(self) -> dict:
        """辞書形式で返す"""
        return {
            "コートValue": self.value,
            "コート名": self.name,
            "申し込み件数": self.applications,
            "残り件数": self.remaining,
        }


@dataclass
class SummaryInfo:
    """合計情報を格納するデータクラス"""

    alltime: int = 0
    zone: int = 0
    count: int = 0

    def to_dict(self) -> dict:
        """辞書形式で返す"""
        return {
            "合計申し込み件数": self.count,
            "合計時間帯": self.zone,
            "合計時間": self.alltime,
        }


class LotteryStatus:
    """複数のCourtInfoを集約・検索・集計するクラス"""

    def __init__(self, court_infos: list[CourtInfo], summary: SummaryInfo):
        self.court_infos = court_infos
        self.summary = summary

    def get_by_name(self, name: str) -> CourtInfo | None:
        return next((ci for ci in self.court_infos if ci.name == name), None)

    def get_by_value(self, value: str | int) -> CourtInfo | None:
        return next(
            (ci for ci in self.court_infos if str(ci.value) == str(value)), None
        )

    def full_courts(self) -> list[CourtInfo]:
        """申し込みが上限に達しているコート"""
        return [ci for ci in self.court_infos if ci.applications >= ci.MAX_APPLICATIONS]

    def available_courts(self) -> list[CourtInfo]:
        """まだ申し込み可能なコート"""
        return [ci for ci in self.court_infos if ci.applications < ci.MAX_APPLICATIONS]
