from unicodedata import normalize
from ..module_base import ModuleBase
from dataclasses import dataclass
from interfaces import LotteryEntry, LotteryStatus, CourtInfo, SummaryInfo
from typing import Iterator
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils import to_datetime


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


class Fetcher(ModuleBase):
    selectors: Selector
    entries_list: list[LotteryEntry] = []
<<<<<<< HEAD
    
    # lotterypage
=======

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    def lottery_status(self) -> LotteryStatus:
<<<<<<< HEAD
        summary_alltime = self.browser.get_element_by_css(self.selectors.STATUS_ALL).text
=======
        # 今取得できるページにいるとして
        summary_alltime = self.browser.get_element_by_css(
            self.selectors.STATUS_ALL
        ).text
>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
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
<<<<<<< HEAD
    # 日付選択のところ
=======

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    def times(self) -> list[int]:
<<<<<<< HEAD
        return [int(normalize("NFKC", time.text[:-2])) for time in self.site.get_element_by_css(self.TIMES)]
    # lottery_list
=======
        return [
            int(normalize("NFKC", time.text[:-2]))
            for time in self.site.get_element_by_css(self.selectors.TIMES)
        ]

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    def entry(self) -> Iterator[LotteryEntry]:
        rows = self.site.get_elements("table.tablebg2 tbody tr")
        for idx, row in enumerate(rows):
            if idx in {0, 1, 7}:
                continue  # ヘッダーとフッターをスキップ
            yield self._parse_row(row)
<<<<<<< HEAD
    # lottery_list
=======

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    def _parse_row(self, row: WebElement) -> LotteryEntry:
        link = self.site.get_element_by_css("内容確認", By.LINK_TEXT, base=row)
        date_text = self.site.get_element_by_css(
            self.selectors.DATE, base=row
        ).text.strip()
        start_text = self.site.get_element_by_css(
            self.selectors.START, base=row
        ).text.strip()
        end_text = self.site.get_element_by_css(
            self.selectors.END, base=row
        ).text.strip()
        court_name = self.site.get_element_by_css(
            self.selectors.COURT, base=row
        ).text.strip()
        # result = self.site.get_element_by_css(self.selectors.RESULT, base=row).text.strip()
        amount_text = self.site.get_element_by_css(
            self.selectors.AMOUNT, base=row
        ).text.strip()

        # データ変換
        date = to_datetime(date_text)
        start = int(start_text.removesuffix("時"))
        end = int(end_text.removesuffix("時"))
        amount = int(amount_text)
        value = self.site.court.to_value(court_name)

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

<<<<<<< HEAD
    
    def __amounts(self) -> list[int]:
        return self.browser.get_elements_by_css(self.selectors.MYPAGE_AMOUNTS)
    # mypage
    def lottery_amount(self) -> int:
        return self.__amounts()[1]
    # mypage
    def reserve_amount(self) -> int:
        return self.__amounts()[0]
=======
    def mypage_amounts(self) -> list[int]:
        eles = self.browser.get_elements_by_css(self.selectors.MYPAGE_AMOUNTS)
        return [int(e.text) for e in eles]

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72