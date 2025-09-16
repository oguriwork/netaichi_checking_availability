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

    # BTN
    BTN_RESERVE = 'input[value="上記の内容で検索する"]'
    BTN_LOGIN = 'input[value="ログイン"]'
    BTN_LOGOUT = 'input[value="ログアウト"]'
    BTN_COURT = 'input[value="対象館一覧を表示"]'
    BTN_AREA = 'input[value="施設決定"]'
    BTN_APPLY = 'input[value="申込みを確定する"]'
    BTN_CECHK = 'input[value="抽選内容を確認する"]'
    BTN_CONFIRM = 'input[value="抽選を申込む"]'
    BTN_DELETE = 'input[value="取消"]'
    BTN_RESELECT_DATE = 'input[value="日時を選びなおす"]'
    BTN_ANOTHER_DATE = 'input[value="別の日時を申込む"]'
    BTN_REVERSE = 'input[value="施設を選びなおす"]'
    BTN_REVERSE2 = 'input[value="条件の選びなおし"]'
    # SELECT
    BTN_COURT2 = 'input[value="選択"]'

    SELECT_AMOUNT = "#selectFieldCnt"
    SELECT_CHECKBOX = 'input[name="selectKomaNo"]'
    SELECT_SPORTS = "#selectPurpose"
    SELECT_PLAYERS = "#applyPepopleNum"

    drawChekcks = ".tablebg2 .s-243m"


class Select(ModuleBase):
    selectors: Selector

    def 未ログイン_エリア(self):
        self.browser.click(self.selectors.BTN_RESERVE)

    def 未ログイン_コート選択(self):
        self.browser.click(self.selectors.BTN_COURT2)

    def court(self, value: str):
        self.browser.select_radio_by_value(value)
        self.browser.click(self.selectors.BTN_COURT)
        # 施設によって細分化されてる場合はここから分岐
        self.browser.click(self.selectors.BTN_AREA)

    def time(self, start, end, span=2):
        times = self.browser.get.times()

        start_i = times.index(start)
        end_i = times.index(end - span)
        checks = [i for i in range(start_i, end_i + 1)]
        check_boxs = self.browser.get_elements_by_css(self.selectors.SELECT_CHECKBOX)
        selected_boxs = [c.is_selected() for c in check_boxs]
        is_enabled = [c.is_enabled() for c in check_boxs]

        if any(is_enabled) is False:
            return False
        if any(selected_boxs):
            for i in range(len(selected_boxs)):
                if selected_boxs[i]:
                    check_boxs[i].click()

        for c in checks:
            if is_enabled[c]:
                check_box = check_boxs[c]
                check_box.click()
            else:
                print(f"checks {checks}")
                print(f"is_enabled[c] {is_enabled[c]}")
                return False
        return True

    def date(self, date):
        self.browser.js_exec(
            f"javascript:selectCalendarDate({date.year},{date.month},{date.day})"
        )

    def amount(self, amount):
        self.browser.select_pulldown(self.selectors.SELECT_AMOUNT, amount)

    def sports(self):
        self.browser.select_by_value(
            self.browser.get_element_by_css(self.selectors.SELECT_SPORTS),
            "1000-10000010",
        )

    def players(self, num):
        self.browser.send_form(self.selectors.SELECT_PLAYERS, num)

    def data(self):
        pass

    def time_checkbox(self):
        pass

    def alert_switch(self):
        pass
