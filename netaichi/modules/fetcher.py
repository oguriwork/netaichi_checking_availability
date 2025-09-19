import re
from dataclasses import dataclass
from datetime import datetime as dd
from typing import Iterator
from unicodedata import normalize

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from interfaces import CourtInfo, LotteryEntry, LotteryStatus, SummaryInfo
from utils import to_datetime

from ..module_base import ModuleBase


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
    # LOTTERY_DATA
    LOTTERY_DATA_DATE = "#useymdLabel"
    LOTTERY_DATA_START = "#stimeLabel"
    LOTTERY_DATA_END = "#etimeLabel"
    LOTTERY_DATA_COURT = "#clsnamem"
    LOTTERY_DATA_AMOUNT = "#field"

    # LOTTERY_CHECK
    LOTTERY_CHECK_DATE = ".in-table td:has(span#targetLabel)"
    LOTTERY_CHECK_COURT = "#clsnamem"
    LOTTERY_CHECK_AMOUNT = "#selectFieldCnt"
    LOTTERY_CHECK_PLAYERS = "#applycnt"


class Fetcher(ModuleBase):
    selectors: Selector
    entries_list: list[LotteryEntry] = []

    # lotterypage
    def lottery_status(self) -> LotteryStatus:
        summary_alltime = self.browser.get_element_by_css(
            self.selectors.STATUS_ALL
        ).text
        summary_zone = self.browser.get_element_by_css(self.selectors.STATUS_ZONE).text
        summary_count = self.browser.get_element_by_css(
            self.selectors.STATUS_COUNT
        ).text
        soup = self.browser.get_html()
        dl = soup.select_one(".smenu > dl")
        if dl is None:
            raise ValueError("court info not found")
        court_names = dl.select("dt")
        court_counts = dl.select("dd")
        court_infos = []
        for name, count in zip(court_names, court_counts):
            name = name.text
            count = int(count.text.split("件")[0])
            if name == "申し込み合計":
                continue
            value = self.site.courts.to_value(name)
            court_info = CourtInfo(value=value, applications=count, name=name)
            court_infos.append(court_info)

        summary = SummaryInfo(
            alltime=int(summary_alltime),
            zone=int(summary_zone),
            count=int(summary_count),
        )
        return LotteryStatus(court_infos=court_infos, summary=summary)

    # 日付選択のところ
    def times(self) -> list[int]:
        return [
            int(normalize("NFKC", time.text[:-2]))
            for time in self.browser.get_elements_by_css(self.selectors.TIMES)
        ]
    def time_checkbox(self) -> list[WebElement]:
        return self.browser.get_elements_by_css(self.selectors.TIMES)


    # lottery_list
    def entry(self) -> Iterator[LotteryEntry]:
        rows = self.browser.get_elements("table.tablebg2 tbody tr")
        for row in rows:
            if row.find_elements(By.CSS_SELECTOR, ":scope > .s-243m"):
                yield self._parse_row(row)

    # lottery_list
    def _parse_row(self, row: WebElement) -> LotteryEntry:
        # 内容確認が input[選択]になる
        link = self.browser.get_element("内容確認", By.PARTIAL_LINK_TEXT, base=row)
        date_text = self.browser.get_element_by_css(
            self.selectors.DATE, base=row
        ).text.strip()
        start_text = self.browser.get_element_by_css(
            self.selectors.START, base=row
        ).text.strip()
        end_text = self.browser.get_element_by_css(
            self.selectors.END, base=row
        ).text.strip()
        court_name = self.browser.get_element_by_css(
            self.selectors.COURT, base=row
        ).text.strip()
        # result = self.browser.get_element_by_css(self.selectors.RESULT, base=row).text.strip()
        amount_text = self.browser.get_element_by_css(
            self.selectors.AMOUNT, base=row
        ).text.strip()

        # データ変換
        date = to_datetime(date_text)
        start = int(start_text.removesuffix("時"))
        end = int(end_text.removesuffix("時"))
        amount = int(amount_text)
        value = self.site.courts.to_value(court_name)

        # 必須項目チェック
        if not all([date, start, end, value, amount]):
            raise ValueError(
                f"必須データが不足: date={date}, start={start}, end={end}, value={value}, amount={amount}"
            )
        return LotteryEntry(
            date=date,
            start=start,
            end=end,
            amount=amount,
            value=value,
            link=link,
            row=row,
        )

    def mypage_amounts(self) -> list[WebElement]:
        return self.browser.get_elements_by_css(self.selectors.MYPAGE_AMOUNTS)

    def confirm_entry(self) -> LotteryEntry:
        court_name = self.browser.get_element_by_css(
            self.selectors.LOTTERY_CHECK_COURT
        ).text
        amount = self.browser.get_element_by_css(
            self.selectors.LOTTERY_CHECK_AMOUNT
        ).text
        d = self.browser.get_element_by_css(self.selectors.LOTTERY_CHECK_DATE).text
        ds = d.split()
        date = dd.strptime(ds[0][:-3], "%Y年%m月%d日")
        times = re.findall(r"([0-9]{1,2})時", d)
        start = int(times[0])
        end = int(times[1])
        value = self.site.court.to_value(court_name)
        return LotteryEntry(
            date=date,
            start=start,
            end=end,
            amount=int(amount),
            value=value,
            link=None,
            row=None,
        )
