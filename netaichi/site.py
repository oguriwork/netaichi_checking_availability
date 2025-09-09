from __future__ import annotations
from browser import ChromeBrowser
import inspect
from .module_base import ModuleBase
import pkgutil
from importlib import import_module
from . import modules
from .error import BrowserErrorController 

class NetAichi:
    def __init__(self, browser: ChromeBrowser):
        self.browser = browser
        self.error_controller = BrowserErrorController(self)

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

    def login(self, account:I_Account) -> None:
        res = self.auth.ensure_login_account(account)
        if res is True:
            self.go.mypage()
        else:
            self.go.login()
            self.auth.login(account)
          
    def logout(self) -> None:
        return self.auth.logout()

    def get_status(self)->LotteryStatus:
        self.go.lottery()
        return self.fetcher.lottery_status()
        
    def yield_lottery_entries(self) -> Iterator[LotteryEntry]:
        for _ in self.go.lottery_list():
            for entry in self.fetcher.lottery_entry():
                yield entry
    
    def all_entries(self) -> list[LotteryEntry]:
        return [e.core() for e in self.yield_lottery_entries()]
    