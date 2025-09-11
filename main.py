from browser import ChromeBrowser
from config import settings
from netaichi import NetAichi
from interfaces.account import I_Account

browser = ChromeBrowser(settings.IS_HEADLESS)
netaichi = NetAichi(browser)


def db_init():
    pass


def reserve():
    pass


# 自分用
def lottry():
    account = I_Account(
        id=settings.ACCOUNT_ID,
        password=ACCOUNT_PASSWORD,
        name="me"
        )
    add_lottery= add_lottery()
    netaichi.login(account)
    netaichi.add_lottery(add_lottery)
    lottery_list = netaichi.get_loettry_list()
    status = netaichi.get_status()
    accounts = gss.get_accounts(account.id)
    for account in accounts:
        netaichi.login(account)
        netaichi.summit_lottery(lottery_list,status)
    


if __name__ == "__main__":
    import sys

    arg = sys.argv[1]

    match arg:
        case "init":
            db_init()
        case "r":
            reserve()
        case "l":
            lottry()
