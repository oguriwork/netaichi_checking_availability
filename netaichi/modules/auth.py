from dataclasses import dataclass
from typing import Optional

from database import M_Account

from ..module_base import ModuleBase
from ._page_status import PAGE_STATUS, update


@dataclass(frozen=True)
class Selector:
    BTN_LOGIN = 'input[value="ログイン"]'
    LOGIN_ID = 'input[name="userId"]'
    LOGIN_PW = "#passwd"


class Auth(ModuleBase):
    selectors: Selector
    logged_account: Optional[M_Account] = None

    @property
    def is_logged_in(self) -> bool:
        return self.logged_account is not None

    @update()
    def login(self, account: M_Account) -> PAGE_STATUS:
        self.browser.send_form(self.selectors.LOGIN_ID, account.id)
        self.browser.send_form(self.selectors.LOGIN_PW, account.password)
        self.browser.click(self.selectors.BTN_LOGIN)
        self.browser.driver.implicitly_wait(3)
        # エラーメッセージで分岐したい
        res = self.site.error.login(account)
        self.logged_account = account
        return PAGE_STATUS.MYPAGE

    @update()
    def logout(self) -> PAGE_STATUS:
        self.site.logout()
        return PAGE_STATUS.TOP

    def ensure_login_account(self, account: M_Account) -> bool:
        if self.logged_account is not None:
            if self.logged_account.id == account.id:
                self.logger.info(f"[OK] ユーザー確認一致: {account.id}")
                return True
            else:
                self.logger.info(
                    f"[!] 他ユーザーでログイン中: {account.id} → ログアウトします。"
                )
                self.logout()
        return False
