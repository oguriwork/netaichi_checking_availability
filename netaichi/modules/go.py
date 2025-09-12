from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from ..module_base import ModuleBase
from ._page_status import PAGE_STATUS, update

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

    @update()
    def top(self) -> PAGE_STATUS:
        self.browser.go_page(self.BASE_URL)
        return PAGE_STATUS.TOP

    @update(via_page=PAGE_STATUS.TOP)
    def login(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.LOGIN)
        return PAGE_STATUS.LOGIN

    @update()
    def logout(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.BTN_LOGOUT)
        self.logged_account = None
        return PAGE_STATUS.TOP

    @update()
    def mypage(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.MYPAGE, 1)
        return PAGE_STATUS.MYPAGE

    @update(via_page=PAGE_STATUS.MYPAGE)
    def lottery(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.LOTTERY)
        return PAGE_STATUS.LOTTERY

    @update(via_page=PAGE_STATUS.MYPAGE)
    def reservation(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.RESERVATION)
        return PAGE_STATUS.RESERVATION

    @update(expected_status=PAGE_STATUS.RESERVATION_LIST, via_page=PAGE_STATUS.MYPAGE)
    def reservation_list(self) -> Generator[int]:
        self.browser.click(self.selectors.LIST, 0)
        return self.loop_list()

    @update(expected_status=PAGE_STATUS.LOTTERY_LIST, via_page=PAGE_STATUS.MYPAGE)
    def lottery_list(self) -> Generator[int]:
        self.browser.click(self.selectors.LIST, 1)
        return self.loop_list()

    def loop_list(self) -> Generator[int]:
        page_index = 1
        yield page_index
        while self.browser.get_html().select(self.selectors.LIST_NEXT) != []:
            page_index += 1
            self.browser.js_exec(f"movePage({page_index});")
            yield page_index

    # requere_status をつけるべき？
    def btn_apply(self) -> PAGE_STATUS:
        """申し込みボタンをクリック"""
        self.browser.click(self.selectors.BTN_APPLY)
        return PAGE_STATUS.RESERVATION

    def btn_check(self) -> PAGE_STATUS:
        """確認ボタンをクリック"""
        self.browser.click(self.selectors.BTN_CHECK)
        return PAGE_STATUS.RESERVATION

    def btn_confirm(self) -> PAGE_STATUS:
        """確定ボタンをクリック"""
        self.browser.click(self.selectors.BTN_CONFIRM)
        return PAGE_STATUS.RESERVATION

    def btn_back(self) -> PAGE_STATUS:
        """戻るボタンをクリック"""
        self.browser.click(self.selectors.BTN_BACK)
        return PAGE_STATUS.RESERVATION_LIST

    @update(via_page=PAGE_STATUS.TOP)
    def notlogin_reserve(self) -> PAGE_STATUS:
        self.browser.click(self.selectors.BTN_NOTLOGIN_RESERVE)
        return PAGE_STATUS.RESERVATION