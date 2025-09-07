from __future__ import annotations
from browser import ChromeBrowser


class ModuleBase:
    def __init__(self, site):
        self.site = site
        self.browser: ChromeBrowser = site.browser
