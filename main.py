from browser import ChromeBrowser
from config import settings
from netaichi import NetAichi

from database import M_Account

browser = ChromeBrowser(settings.IS_HEADLESS)
netaichi = NetAichi(browser)


def db_init():
    pass


def reserve():
    pass


def test():
    account = M_Account(
        id=settings.ACCOUNT_ID, password=settings.ACCOUNT_PASSWORD, name="me"
    )
    netaichi.login(account)
    for _ in netaichi.go.reservation_list():
        input("next?")
    netaichi.logout()


# 自分用
def lottry():
    account = M_Account(
        id=settings.ACCOUNT_ID, password=settings.ACCOUNT_PASSWORD, name="me"
    )
    netaichi.login(account)
    add_lottery()


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
        case _:
            test()
