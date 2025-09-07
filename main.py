from browser import ChromeBrowser
from config import settings
from netaichi import NetAichi

browser = ChromeBrowser(settings.IS_HEADLESS)
netaichi = NetAichi(browser)


def db_init():
    pass


def reserve():
    pass


# 自分用
def lottry():
    pass


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
