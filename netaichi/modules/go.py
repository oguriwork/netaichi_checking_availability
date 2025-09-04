from __future__ import annotations
from collections.abc import Generator
from ..module_base import ModuleBase
from ._go_status import PAGE_STATUS, update


class Go(ModuleBase):
    current_page = None
    LOGIN = "#login"
    MYPAGE = 'table[width="850"] td>a'  # [1]
    RESERVATION = "#goNameSearch"
    LOTTERY = "#goLotSerach"
    LIST = ".s-241m>a"
    BTN_LOGIN = 'input[value="ログイン"]'
    BTN_LOGOUT = 'input[value="ログアウト"]'
    LIST_NEXT = "#goNextPager"
    BTN_APPLY = 'input[value="申し込み"]'
    BTN_CHECK = 'input[value="確認"]'
    BTN_CONFIRM = 'input[value="確定"]'
    BTN_BACK = 'input[value="戻る"]'

    # allow_anonymous
    @update
    def login(self) -> PAGE_STATUS:
        self.site.go_page(self.site.BASE_URL)
        self.site.click(self.LOGIN)
        return PAGE_STATUS.LOGIN

    @update
    def logout(self) -> PAGE_STATUS:
        self.site.click(self.BTN_LOGOUT)
        return PAGE_STATUS.LOGOUT

    @update
    def mypage(self) -> PAGE_STATUS:
        self.site.click(self.MYPAGE, 1)
        return PAGE_STATUS.MYPAGE

    @update
    def lottery(self) -> PAGE_STATUS:
        self.site.click(self.LOTTERY)
        return PAGE_STATUS.LOTTERY

    @update
    def reservation(self) -> PAGE_STATUS:
        self.site.click(self.RESERVATION)
        return PAGE_STATUS.RESERVATION

    @update(PAGE_STATUS.RESERVATION_LIST)
    def reservation_list(self) -> Generator[int]:
        self.site.click(self.LIST, 0)
        return self.loop_list()

    @update(PAGE_STATUS.LOTTERY_LIST)
    def lottery_list(self) -> Generator[int]:
        self.site.click(self.LIST, 1)
        return self.loop_list()

    def loop_list(self) -> Generator[int]:
        page_index = 1
        yield page_index
        while self.site.get_html().select(self.LIST_NEXT) != []:
            page_index += 1
            self.site.js_exec(f"movePage({page_index});")
            yield page_index

    # return 適当
    def btn_apply(self) -> PAGE_STATUS:
        """申し込みボタンをクリック"""
        self.site.click(self.BTN_APPLY)
        return PAGE_STATUS.RESERVATION

    def btn_check(self) -> PAGE_STATUS:
        """確認ボタンをクリック"""
        self.site.click(self.BTN_CHECK)
        return PAGE_STATUS.RESERVATION

    def btn_confirm(self) -> PAGE_STATUS:
        """確定ボタンをクリック"""
        self.site.click(self.BTN_CONFIRM)
        return PAGE_STATUS.RESERVATION

    def btn_back(self) -> PAGE_STATUS:
        """戻るボタンをクリック"""
        self.site.click(self.BTN_BACK)
        return PAGE_STATUS.RESERVATION_LIST

    def notlogin_reserve(self):
        self.site.go_page(self.site.BASE_URL)
        BTN_NOTLOGIN_RESERVE = "#facility02_on"
        self.site.click(BTN_NOTLOGIN_RESERVE)
