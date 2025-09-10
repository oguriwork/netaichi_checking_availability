from ..module_base import ModuleBase
from ._go_status import PAGE_STATUS, update
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
    MYPAGE_AMOUNTS = '#lotNum'

class Fetcher(ModuleBase):
    entries_list: list[LotteryEntry] = []
    
    def lottery_status(self) -> LotteryStatus:
        # 今取得できるページにいるとして
        summary_alltime = self.browser.get_element_by_css(self.selectors.STATUS_ALL).text
        summary_zone = self.browser.get_element_by_css(self.selectors.STATUS_ZONE).text
        summary_count = self.browser.get_element_by_css(self.selectors.STATUS_COUNT).text
        soup = self.browser.get_html()
        dl = soup.select_one(".smenu > dl")
        court_names = dl.select("dt")
        court_counts = dl.select("dd")
        court_infos = []
        for name, count in zip(court_names, court_counts):
            name = name.text
            count = int(count.text.split("件")[0])
            if name == "申し込み合計":
                continue
            value = self.site.court.to_value(name)
            court_info = CourtInfo(value=value, applications=count)
            court_infos.append(court_info)

        summary = SummaryInfo(alltime=summary_alltime, zone=summary_zone, count=summary_count)
        return LotteryStatus(court_infos=court_infos, summary=summary)
    def times(self) -> list[int]:
        return [int(normalize("NFKC", time.text[:-2])) for time in self.site.get_element_by_css(self.TIMES)]
    def entry(self) -> Iterator[LotteryEntry]:
        rows = self.site.get_elements("table.tablebg2 tbody tr")
        for idx, row in enumerate(rows):
            if idx in {0, 1, 7}:
                continue  # ヘッダーとフッターをスキップ
            yield self._parse_row(row)
    
    def _parse_row(self, row: WebElement) -> LotteryEntry:
        link = self.site.get_element_by_css("内容確認", By.LINK_TEXT, base=row)
        date_text = self.site.get_element_by_css(self.selectors.DATE, base=row).text.strip()
        start_text = self.site.get_element_by_css(self.selectors.START, base=row).text.strip()
        end_text = self.site.get_element_by_css(self.selectors.END, base=row).text.strip()
        court_name = self.site.get_element_by_css(self.selectors.COURT, base=row).text.strip()
        # result = self.site.get_element_by_css(self.selectors.RESULT, base=row).text.strip()
        amount_text = self.site.get_element_by_css(self.selectors.AMOUNT, base=row).text.strip()

        # データ変換
        date = to_datetime(date_text)
        start = int(start_text.removesuffix("時"))
        end = int(end_text.removesuffix("時"))
        amount = int(amount_text)
        value = self.site.court.to_value(court_name)

        # 必須項目チェック
        if not all([date, start, end, value, amount]):
            raise ValueError(f"必須データが不足: date={date}, start={start}, end={end}, value={value}, amount={amount}")

        return LotteryEntry(
            date=date,
            start=start,
            end=end,
            amount=amount,
            value=value,
            link=link,
            row=row,
        )

    

    def mypage_amounts(self) -> list[int]:
        return self.browser.get_elements_by_css(self.selectors.MYPAGE_AMOUNTS)