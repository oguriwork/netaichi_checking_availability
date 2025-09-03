from __future__ import annotations

from enum import Enum
from typing import Any

from selenium import webdriver
from selenium.webdriver import Chrome as WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from core.utils import AppLogger

from .deco import ensure_driver_exists, randam_sleep
from .errors import ElementNotFoundError




class ChromeBrowser:
    driver: WebDriver
    LOGGER_NAME = "ChromeBrowser"

    def __init__(self, is_headless: bool = True, default_timeout: int = 10) -> None:
        self.is_headless = is_headless
        self.default_timeout = default_timeout
        self.logger = AppLogger(self.LOGGER_NAME)
        self.new()

    @property
    @ensure_driver_exists
    def current_url(self) -> str:
        return self.driver.current_url

    def __enter__(self) -> ChromeBrowser:
        if not self.driver:
            self.new()
        return self

    def __exit__(self, ex_type: type | None, ex_value: Exception | None, trace: Any | None) -> None:
        self.quit()

    def new(self) -> WebDriver:
        from core.config.browser import OPTIONS

        options = webdriver.ChromeOptions()
        if self.is_headless:
            options.add_argument("--headless=new")

        for option in OPTIONS:
            options.add_argument(option)

        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        options.timeouts = {"implicit": self.default_timeout * 1000}

        self.driver = webdriver.Chrome(options=options)

        self.js_exec("delete Object.getPrototypeOf(navigator).webdriver;")

        self.logger.info("Chrome browser initialized successfully")
        return self.driver

    def quit(self) -> None:
        if self.driver:
            self.driver.quit()
            self.logger.info("Chrome browser closed successfully")
            del self.driver

    @randam_sleep
    @ensure_driver_exists
    def go_page(self, url: str) -> None:
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")

    @randam_sleep
    @ensure_driver_exists
    def send_form(self, selector: str, value: str) -> bool:
        if not isinstance(value, str):
            value = str(value)

        element = self.get_element_by_css(selector)
        if element:
            element.clear()
            element.send_keys(value)
            self.logger.info(f"Form field '{selector}' filled with value")
            return True
        return False

    @randam_sleep
    @ensure_driver_exists
    def click(self, selector: str, index: int = 0) -> None:
        if index < 0:
            raise ValueError("Index must be non-negative")

        element = self.get_element_by_css(selector, index)
        if not element:
            raise ElementNotFoundError(f"Element not found for selector: {selector}")

        element.click()
        self.logger.info(f"Clicked element: {selector}[{index}]")

    @randam_sleep
    @ensure_driver_exists
    def alert_switch(self, accept: bool) -> None:
        self.wait_alert(3)
        if accept:
            self.driver.switch_to.alert.accept()
            self.logger.info("Alert accepted")
        else:
            self.driver.switch_to.alert.dismiss()
            self.logger.info("Alert dismissed")

    @randam_sleep
    @ensure_driver_exists
    def wait_alert(self, timeout: int = 3) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be positive")

        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())

    @randam_sleep
    @ensure_driver_exists
    def js_exec(self, code: str) -> Any:
        if not code or not isinstance(code, str):
            raise ValueError("JavaScript code must be a non-empty string")

        result = self.driver.execute_script(code)
        self.logger.info("JavaScript executed successfully")
        return result

    @randam_sleep
    @ensure_driver_exists
    def drag_and_drop(self, source: WebElement, target_selector: str) -> None:
        if not isinstance(source, WebElement):
            raise ValueError("Source must be a WebElement")

        target = self.get_element_by_css(target_selector)
        if not target:
            raise ElementNotFoundError(f"Drop target not found: {target_selector}")

        actions = ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.perform()
        self.logger.info(f"Drag and drop completed to: {target_selector}")

    @randam_sleep
    @ensure_driver_exists
    def scroll_into_view(self, selector: str, position: ScrollPosition = ScrollPosition.START) -> None:
        if not isinstance(position, ScrollPosition):
            raise ValueError("Position must be a ScrollPosition enum value")

        element = self.get_element_by_css(selector)
        if not element:
            raise ElementNotFoundError(f"Element not found for scrolling: {selector}")

        self.driver.execute_script(f'arguments[0].scrollIntoView({{block: "{position.value}"}});', element)
        self.logger.info(f"Scrolled element into view: {selector}")

    @ensure_driver_exists
    def get_elements(
        self, selector: str, by: str = By.CSS_SELECTOR, base: WebElement | None = None
    ) -> list[WebElement]:
        if not selector or not isinstance(selector, str):
            raise ValueError("Selector must be a non-empty string")

        if base and not isinstance(base, WebElement):
            raise ValueError("Base must be a WebElement or None")

        if base:
            elements = base.find_elements(by, selector)
        else:
            elements = self.driver.find_elements(by, selector)

        return elements

    def get_element(self, selector: str, by: str, index: int = 0, base: WebElement | None = None) -> WebElement:
        if index < 0:
            raise ValueError("Index must be non-negative")

        elements = self.get_elements(selector, by, base)
        if not elements or index >= len(elements):
            raise ElementNotFoundError(f"Element not found for selector: {selector} with index: {index}")

        return elements[index]

    def get_elements_by_css(self, css_selector: str, base: WebElement | None = None) -> list[WebElement]:
        return self.get_elements(css_selector, By.CSS_SELECTOR, base)

    def get_element_by_css(
        self, css_selector: str, index: int = 0, base: WebElement | None = None
    ) -> WebElement | None:
        return self.get_element(css_selector, By.CSS_SELECTOR, index, base)

    def get_elements_by_contains_text(self, path: str, text: str, base: WebElement | None = None) -> list[WebElement]:
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")

        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        xpath = f".{path}[contains(text(), '{text}')]"
        return self.get_elements(xpath, By.XPATH, base)

    def get_element_by_contains_text(
        self, path: str, text: str, index: int = 0, base: WebElement | None = None
    ) -> WebElement | None:
        elements = self.get_elements_by_contains_text(path, text, base)
        if not elements or index >= len(elements):
            return None

        return elements[index]

    def get_element_by_xpath(self, xpath: str, index: int = 0, base: WebElement | None = None) -> WebElement | None:
        return self.get_element(xpath, By.XPATH, index, base)

    def get_elements_by_xpath(self, xpath: str, base: WebElement | None = None) -> list[WebElement]:
        return self.get_elements(xpath, By.XPATH, base)

    def select_by_index(self, select_element: WebElement, index: int) -> None:
        if not isinstance(select_element, WebElement):
            raise ValueError("Select element must be a WebElement")

        if index < 0:
            raise ValueError("Index must be non-negative")

        Select(select_element).select_by_index(index)

    def select_by_value(self, select_element: WebElement, value: str) -> None:
        if not isinstance(select_element, WebElement):
            raise ValueError("Select element must be a WebElement")

        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        Select(select_element).select_by_value(value)

    def select_by_visible_text(self, select_element: WebElement, text: str) -> None:
        if not isinstance(select_element, WebElement):
            raise ValueError("Select element must be a WebElement")

        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        Select(select_element).select_by_visible_text(text)

    def select_pulldown(self, selector: str, index: int) -> None:
        if index < 1:
            raise ValueError("Index must be 1 or greater")

        element = self.get_element_by_css(selector)
        if not element:
            raise ElementNotFoundError(f"Select element not found for selector: {selector}")

        self.select_by_index(element, index - 1)

    def get_input_value(self, value: str) -> WebElement:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        ele = self.get_element_by_css(f'input[value="{value}"]')
        if not ele:
            raise ElementNotFoundError(f"Radio button not found for value: {value}")
        return ele

    def select_radio_by_value(self, value: str) -> None:
        radio = self.get_input_value(value)
        radio.send_keys(Keys.SPACE)

    @ensure_driver_exists
    def refresh_page(self) -> None:
        self.driver.refresh()
        self.logger.info("Page refreshed")

    @ensure_driver_exists
    def go_back(self) -> None:
        self.driver.back()
        self.logger.info("Navigated back")

    @ensure_driver_exists
    def go_forward(self) -> None:
        self.driver.forward()
        self.logger.info("Navigated forward")
