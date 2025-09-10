from ..module_base import ModuleBase
from interface import I_Account
from ._go_status import PAGE_STATUS, update
from dataclasses import dataclass

@dataclass(frozen=True)
class Selector:
    BTN_LOGIN = 'input[value="ログイン"]'
    LOGIN_ID = 'input[name="userId"]'
    LOGIN_PW = "#passwd"

class Auth(ModuleBase):
    logged_account: I_Account | None = None
    

    @property
    def is_logged(self) -> bool:
        return self.logged_account is not None

    @update
    def login(self, account: I_Account) -> bool:
        self.browser.send_form(self.selectors.LOGIN_ID, account.id)
        self.browser.send_form(self.selectors.LOGIN_PW, account.password)
        self.browser.click(self.selectors.BTN_LOGIN)
        self.browser.driver.implicitly_wait(3)
        # エラーメッセージで分岐したい
        res =self.site.error_controller.login(account)
        self.logged_account = account
        return PAGE_STATUS.LOGGED_IN

    def logout(self):
        return self.site.logout()
    

    def ensure_login_account(self,account:I_Account)->None:
        if self.is_logged:
            if self.logged_account.id == account.id:
                print(f"[OK] ユーザー確認一致: {account.id}")
                return True
            else:
                print(f"[!] 他ユーザーでログイン中: {account.id} → ログアウトします。")
                self.logout()