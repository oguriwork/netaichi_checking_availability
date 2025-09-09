from ..module_base import ModuleBase
from interface import I_Account
from ._go_status import PAGE_STATUS, update

class Auth(ModuleBase):
    logged_account: I_Account | None = None
    SELECTER_BTN_LOGIN = 'input[value="ログイン"]'
    SELECTER_LOGIN_ID = 'input[name="userId"]'
    SELECTER_LOGIN_PW = "#passwd"

    @property
    def is_logged(self) -> bool:
        return self.logged_account is not None

    @update
    def login(self, account: I_Account) -> bool:
        self.browser.send_form(self.SELECTER_LOGIN_ID, account.id)
        self.browser.send_form(self.SELECTER_LOGIN_PW, account.password)
        self.browser.click(self.SELECTER_BTN_LOGIN)
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