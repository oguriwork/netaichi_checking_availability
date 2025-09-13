from enum import Enum, auto
from functools import wraps
from typing import Optional


class PAGE_STATUS(Enum):
    MYPAGE = auto()
    LOTTERY = auto()
    LOTTERY_LIST = auto()
    RESERVATION = auto()
    RESERVATION_LIST = auto()
    CALENDAR = auto()
    LOGIN = auto()
    ERROR = auto()
    TOP = auto()
    LOGOUT = auto()
    LOGGED_IN = auto()

    def __str__(self):
        return self.name.lower()


def update(
    expected_status: Optional[PAGE_STATUS] = None,
    *,
    via_page: Optional[PAGE_STATUS] = None,
):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # すでに目的のページにいるならスキップ
            if expected_status and self.current_page == expected_status:
                self.browser.logger.debug(
                    f"すでに {expected_status} にいるため {func.__name__} をスキップ"
                )
                return self.current_page

            # 経由する必要がある場合のみ
            if via_page == PAGE_STATUS.MYPAGE != self.current_page:
                self.mypage()
            if via_page == PAGE_STATUS.TOP != self.current_page:
                self.top()

            old_url = self.browser.current_url
            result = func(self, *args, **kwargs)

            # 戻り値が PAGE_STATUS の場合は更新
            if isinstance(result, PAGE_STATUS):
                if old_url != self.browser.current_url:
                    self.browser.logger.debug(f"ページ遷移: {result}")
                    self.browser.logger.debug(
                        f"{old_url} -> {self.browser.current_url}"
                    )
                self.current_page = result
            return result or self.current_page

        return wrapper

    return decorator


def require_status(*allowed_statuses: PAGE_STATUS):
    """
    指定したステータス以外では呼べないようにするデコレーター
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.current_page not in allowed_statuses:
                raise RuntimeError(
                    f"{func.__name__} は {', '.join(map(str, allowed_statuses))} "
                    f"の状態でしか呼べません。現在の状態: {self.current_page}"
                )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
