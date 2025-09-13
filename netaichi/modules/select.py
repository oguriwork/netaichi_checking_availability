from ..module_base import ModuleBase
from dataclasses import dataclass


@dataclass(frozen=True)
class Selector:
    DATE = "#useymdLabel"
    START = "#stimeLabel"
    END = "#etimeLabel"
    COURT = "#clsnamem"
    AMOUNT = "#field"
    RESULT = "#lotStateLabel"
    TIMES = "#komanamem"
    # STATUS
    STATUS_COUNT = "#allCount"  # 件数
    STATUS_ZONE = "#allTzonecnt"  # 時間帯
    STATUS_ALL = "#allTimeLabel"  # 合計時間
    MYPAGE_AMOUNTS = "#lotNum"


class Select(ModuleBase):

    def court(self):
        pass
    def data(self):
        pass
    def amount(self):
        pass
    def sports(self):
        pass
    def time_checkbox(self):
        pass
    def alert_switch(self):
        pass
    