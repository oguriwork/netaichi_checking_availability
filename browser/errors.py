from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)


class BrowserError(Exception):
    pass


class ElementNotFoundError(BrowserError):
    pass


class ElementNotInteractableError(BrowserError):
    pass


class BrowserNotInitializedError(BrowserError):
    pass
