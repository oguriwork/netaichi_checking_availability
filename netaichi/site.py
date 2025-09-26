from __future__ import annotations

import inspect
import pkgutil
from importlib import import_module
from typing import Iterator

from .courts import CourtManager

from browser import ChromeBrowser

# from .error import BrowserErrorController
from database import M_Account
from interfaces import LotteryEntry, LotteryStatus

from . import modules
from .module_base import ModuleBase
from .modules import PAGE_STATUS, Auth, Fetcher, Go
from .error_handler import ErrorHandler


class NetAichi:
    auth: Auth
    go: Go
    fetcher: Fetcher
    browser: ChromeBrowser
    select: ModuleBase
    error_handler: ErrorHandler
    LOTTERY_MONTH = 3

    def __init__(self, browser: ChromeBrowser):
        self.browser = browser
        self.courts = CourtManager(self.LOTTERY_MONTH)
        self.error_handler = ErrorHandler(self)

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
            self.go.mypage()  # type: ignore
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
        return self.fetcher.mypage_amounts()
       

    def lottery_amount(self) -> int:
        return self.__get_amount()[1]

    def reserve_amount(self) -> int:
        return self.__get_amount()[0]

    def submit_lottery_entries(self, entries: list[LotteryEntry], status, player: int):
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
                
                self.select.time_checkbox(
                    self.fetcher.time_checkbox(),
                    entry.start,
                    entry.end,
                )
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

    def is_entry_verified(self, entry: LotteryEntry) -> bool:
        confirm_entry = self.fetcher.lottery.confirm_entry()
        return confirm_entry == entry

    def yield_reserve_(self):
        # LotteryEntryを共通化したらいけるんちゃう？
        for _ in self.go.reservation_list():
            soup = self.browser.get_html()
            dates = soup.select(Selecter.RESERVE_DATA_DATE)
            courts = soup.select(Selecter.RESERVE_DATA_COURT)
            if len(dates) != len(courts):
                raise RuntimeError(ErrorMessage.RESERVATION_DATA)
            for i in range(len(dates)):
                date_split = normalize('NFKD', dates[i].text).split(' ')
                court_split = normalize('NFKD', courts[i].text).split(' ')
                date = self.jsp.to_datetime(date_split[0])
                # week = date_split[1]
                start = date_split[2].removesuffix('時')
                end = date_split[4].removesuffix('時')
                court = court_split[0]
                court_number = court_split[2][court_split[2].find(
                    '場')+1:court_split[2].find('(')]
                temp.append({
                    'court': court,
                    'court_number': court_number,
                    'date': date,
                    'start': start,
                    'end': end,
                    'account': self.jsp.logged_account.id
                })