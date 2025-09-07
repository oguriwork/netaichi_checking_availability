from ..module_base import ModuleBase
from interface import I_Account


class Auth(ModuleBase):
    logged_accounts: I_Account | None = None
    SELECTER_BTN_LOGIN = 'input[value="ログイン"]'
    SELECTER_LOGIN_ID = 'input[name="userId"]'
    SELECTER_LOGIN_PW = "#passwd"

    @property
    def is_logged(self) -> bool:
        return self.logged_accounts is not None

    def login(self, account: I_Account) -> bool:
        self.site.go.login()
        self.browser.send_form(self.SELECTER_LOGIN_ID, account.id)
        self.browser.send_form(self.SELECTER_LOGIN_PW, account.password)
        self.browser.click(self.SELECTER_BTN_LOGIN)
        self.browser.driver.implicitly_wait(3)
        self.site.check_error()
        self.logged_accounts = account
        return True
