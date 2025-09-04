from __future__ import annotations
from browser import ChromeBrowser
import inspect
from .module_base import ModuleBase
import pkgutil
from importlib import import_module
from . import modules


class NetAichi:
    def __init__(self, browser: ChromeBrowser):
        self.browser = browser

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
