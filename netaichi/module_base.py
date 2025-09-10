from __future__ import annotations
from browser import ChromeBrowser
import sys
import inspect


class ModuleBase:
    def __init__(self, site):
        self.site = site
        self.browser: ChromeBrowser = site.browser

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        module = sys.modules[cls.__module__]

        # 同じファイルの "Selector" クラスを探す
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name == "Selector":
                cls.selectors = obj()  # インスタンス化してクラス属性にセット
                break
