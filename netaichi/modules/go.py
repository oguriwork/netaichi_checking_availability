from __future__ import annotations
from collections.abc import Generator
from ..module_base import ModuleBase
from ._page_status import PAGE_STATUS, update
from dataclasses import dataclass


@dataclass(frozen=True)
class Selector:
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
    BTN_NOTLOGIN_RESERVE = 'input[value="ログインせずに申し込む"]'


class Go(ModuleBase):
    selectors: Selector
    current_page = None
    BASE_URL = "https://www4.pref.aichi.jp/yoyaku/"
<<<<<<< HEAD
    
    @update
=======

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    def top(self) -> PAGE_STATUS:
        self.site.go_page(self.site.BASE_URL)
        return PAGE_STATUS.TOP
<<<<<<< HEAD

=======

    # allow_anonymous
>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    @update
    def login(self) -> PAGE_STATUS:
        self.top()
        self.site.click(self.selectors.LOGIN)
        return PAGE_STATUS.LOGIN

    @update
    def logout(self) -> PAGE_STATUS:
        self.site.click(self.selectors.BTN_LOGOUT)
        self.logged_account = None
        return PAGE_STATUS.TOP
<<<<<<< HEAD
        
=======

>>>>>>> caf4679860b0e598561114f5e8efcc38d5fabf72
    @update
    def mypage(self) -> PAGE_STATUS:
        self.site.click(self.selectors.MYPAGE, 1)
        return PAGE_STATUS.MYPAGE

    @update(via_mypage=True)
    def lottery(self) -> PAGE_STATUS:
        self.site.click(self.selectors.LOTTERY)
        return PAGE_STATUS.LOTTERY

    @update(via_mypage=True)
    def reservation(self) -> PAGE_STATUS:
        self.site.click(self.selectors.RESERVATION)
        return PAGE_STATUS.RESERVATION

    @update(PAGE_STATUS.RESERVATION_LIST, via_mypage=True)
    def reservation_list(self) -> Generator[int]:
        self.site.click(self.selectors.LIST, 0)
        return self.loop_list()

    @update(PAGE_STATUS.LOTTERY_LIST, via_mypage=True)
    def lottery_list(self) -> Generator[int]:
        self.site.click(self.selectors.LIST, 1)
        return self.loop_list()

    def loop_list(self) -> Generator[int]:
        page_index = 1
        yield page_index
        while self.site.get_html().select(self.selectors.LIST_NEXT) != []:
            page_index += 1
            self.site.js_exec(f"movePage({page_index});")
            yield page_index

    # return 適当
    def btn_apply(self) -> PAGE_STATUS:
        """申し込みボタンをクリック"""
        self.site.click(self.selectors.BTN_APPLY)
        return PAGE_STATUS.RESERVATION

    def btn_check(self) -> PAGE_STATUS:
        """確認ボタンをクリック"""
        self.site.click(self.selectors.BTN_CHECK)
        return PAGE_STATUS.RESERVATION

    def btn_confirm(self) -> PAGE_STATUS:
        """確定ボタンをクリック"""
        self.site.click(self.selectors.BTN_CONFIRM)
        return PAGE_STATUS.RESERVATION

    def btn_back(self) -> PAGE_STATUS:
        """戻るボタンをクリック"""
        self.site.click(self.selectors.BTN_BACK)
        return PAGE_STATUS.RESERVATION_LIST

    def notlogin_reserve(self):
        self.top()
        self.site.click(self.selectors.BTN_NOTLOGIN_RESERVE)
