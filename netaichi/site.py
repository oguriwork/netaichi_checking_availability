from __future__ import annotations
from browser import ChromeBrowser
import inspect
from .module_base import ModuleBase
import pkgutil
from importlib import import_module
from . import modules
#from .error import BrowserErrorController
from database import M_Account
from .modules import Auth, Go, Fetcher, PAGE_STATUS
from interfaces import LotteryEntry, LotteryStatus
from typing import Iterator


class NetAichi:
    auth: Auth
    go: Go
    fetcher: Fetcher
    browser: ChromeBrowser

    def __init__(self, browser: ChromeBrowser):
        self.browser = browser
        #self.error_controller = BrowserErrorController(self)

        # modules/ 以下のモジュールを探索
        for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
            # 先頭が "_" のものは読み込まない
            if module_name.startswith("_"):
                continue
            mod = import_module(f"{modules.__name__}.{module_name}")
            # ModuleBase を継承しているクラスを探す
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, ModuleBase) and obj is not ModuleBase:
                    setattr(self, name.lower(), obj(self))

    def login(self, account: M_Account) -> None:
        res = self.auth.ensure_login_account(account)
        if res is True:
            self.go.mypage() # type: ignore
        else:
            self.go.login()
            self.auth.login(account)

    def logout(self) -> PAGE_STATUS:
        return self.go.logout()

    def get_status(self) -> LotteryStatus:
        self.go.lottery()
        return self.fetcher.lottery_status()

    def yield_lottery_entries(self) -> Iterator[LotteryEntry]:
        for _ in self.go.lottery_list():
            for entry in self.fetcher.lottery_entry():
                yield entry

    def all_entries(self) -> list[LotteryEntry]:
        return [e.core() for e in self.yield_lottery_entries()]
    

    def __get_amount(self) -> list[int]:
        self.go.mypage()
        elements = self.fetcher.mypage_amounts()
        return elements

    def lottery_amount(self) -> int:
        return self.__get_amount()[1]

    def reserve_amount(self) -> int:
        return self.__get_amount()[0]

    def submit_lottery_entries(self,entries:list[LotteryEntry],status,player:int)
        # 現在ログインしているアカウントで登録
        # 未完成
        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry.value].append(entry)
        for value, group in sorted(grouped.items()):
            self.go.lottery()
            self.select.court(value)
            for entry in group:
                if entry.account_group != self.auth.logged_account.id:
                    continue 
                self.select.date(entry.date)
                self.select.amount(entry.amount)
                self.select.time_checkbox(entry.start,entry.end,)
                # 申し込みボタンクリック
                self.go.BTN_APPLY()
                self.select.sports("tennis")
                self.select.players(players)
                # 確認ボタンクリック  
                self.go.BTN_CHECK()
                if self.is_entry_verified() is False:
                    input(entry)
                    raise RuntimeError("予定と違う")
                # 確定ボタンクリック
                self.go.BTN_CONFIRM()            
                self.select.alert_switch(True)
                # errorメッセージ確認

    def is_entry_verified(self,entry:LotteryEntry) -> bool:
        confirm_entry= self.fetcher.lottery.confirm_entry()
        return confirm_entry == entry 
    