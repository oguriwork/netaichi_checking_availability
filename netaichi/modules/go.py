from __future__ import annotations
from collections.abc import Generator
from ..module_base import ModuleBase
from ._go_status import PAGE_STATUS, update,require_status


class Go(ModuleBase):
    current_page = None
    BASE_URL = "https://www4.pref.aichi.jp/yoyaku/"
    SELECTER_LOGIN = "#login"
    SELECTER_MYPAGE = 'table[width="850"] td>a'  # [1]
    SELECTER_RESERVATION = "#goNameSearch"
    SELECTER_LOTTERY = "#goLotSerach"
    SELECTER_LIST = ".s-241m>a"
    SELECTER_BTN_LOGIN = 'input[value="ログイン"]'
    SELECTER_BTN_LOGOUT = 'input[value="ログアウト"]'
    SELECTER_LIST_NEXT = "#goNextPager"
    SELECTER_BTN_APPLY = 'input[value="申し込み"]'
    SELECTER_BTN_CHECK = 'input[value="確認"]'
    SELECTER_BTN_CONFIRM = 'input[value="確定"]'
    SELECTER_BTN_BACK = 'input[value="戻る"]'

    # allow_anonymous
    @update
    def login(self) -> PAGE_STATUS:
        self.site.go_page(self.site.BASE_URL)
        self.site.click(self.SELECTER_LOGIN)
        return PAGE_STATUS.LOGIN

    @update
    def logout(self) -> PAGE_STATUS:
        self.site.click(self.SELECTER_BTN_LOGOUT)
        return PAGE_STATUS.LOGOUT

    @update
    def mypage(self) -> PAGE_STATUS:
        self.site.click(self.SELECTER_MYPAGE, 1)
        return PAGE_STATUS.MYPAGE

    @update(via_mypage=True)
    def lottery(self) -> PAGE_STATUS:
        self.site.click(self.SELECTER_LOTTERY)
        return PAGE_STATUS.LOTTERY

    @update(via_mypage=True)
    def reservation(self) -> PAGE_STATUS:
        self.site.click(self.SELECTER_RESERVATION)
        return PAGE_STATUS.RESERVATION

    @update(PAGE_STATUS.RESERVATION_LIST,via_mypage=True)
    def reservation_list(self) -> Generator[int]:
        self.site.click(self.SELECTER_LIST, 0)
        return self.loop_list()

    @update(PAGE_STATUS.LOTTERY_LIST,via_mypage=True)
    def lottery_list(self) -> Generator[int]:
        self.site.click(self.SELECTER_LIST, 1)
        return self.loop_list()

    def loop_list(self) -> Generator[int]:
        page_index = 1
        yield page_index
        while self.site.get_html().select(self.SELECTER_LIST_NEXT) != []:
            page_index += 1
            self.site.js_exec(f"movePage({page_index});")
            yield page_index

    # return 適当
    def btn_apply(self) -> PAGE_STATUS:
        """申し込みボタンをクリック"""
        self.site.click(self.SELECTER_BTN_APPLY)
        return PAGE_STATUS.RESERVATION

    def btn_check(self) -> PAGE_STATUS:
        """確認ボタンをクリック"""
        self.site.click(self.SELECTER_BTN_CHECK)
        return PAGE_STATUS.RESERVATION

    def btn_confirm(self) -> PAGE_STATUS:
        """確定ボタンをクリック"""
        self.site.click(self.SELECTER_BTN_CONFIRM)
        return PAGE_STATUS.RESERVATION

    def btn_back(self) -> PAGE_STATUS:
        """戻るボタンをクリック"""
        self.site.click(self.SELECTER_BTN_BACK)
        return PAGE_STATUS.RESERVATION_LIST

    def notlogin_reserve(self):
<<<<<<< HEAD
        self.site.go_page(self.BASE_URL)
        BTN_NOTLOGIN_RESERVE = "#facility02_on"
        self.site.click(BTN_NOTLOGIN_RESERVE)
=======
        self.top()
        
        self.site.click(self.BTN_NOTLOGIN_RESERVE)
>>>>>>> fb0942951f1217181f0921aa9d475c53747c43c4
