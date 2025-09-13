from __future__ import annotations
from ..module_base import ModuleBase
from dataclasses import dataclass
from enum import Enum, auto
from selenium.webdriver.remote.webelement import WebElement
from database import M_Account


@dataclass(frozen=True)
class Selector:
    LOGIN_ERROR_MESSAGE = "#allMessages2"
    GENERAL_ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    WARNING_MESSAGE = ".warning-message"


class ErrorResult(Enum):
    """エラー処理結果を表す列挙型"""

    SUCCESS = auto()
    RETRY = auto()
    FAIL = auto()
    EXPIRED = auto()
    UNKNOWN = auto()
    RECAPTCHA = auto()
    MAINTENANCE = auto()
    NETWORK_ERROR = auto()
    TIMEOUT = auto()
    CAPTCHA_REQUIRED = auto()
    ACCOUNT_LOCKED = auto()
    INVALID_SESSION = auto()
    INVALID_CREDENTIALS = auto()

    def __str__(self):
        return self.name.lower()

    @property
    def is_recoverable(self) -> bool:
        """リトライ可能なエラーかどうかを判定"""
        return self in {
            ErrorResult.RETRY,
            ErrorResult.RECAPTCHA,
            ErrorResult.NETWORK_ERROR,
            ErrorResult.TIMEOUT,
            ErrorResult.CAPTCHA_REQUIRED,
            ErrorResult.INVALID_SESSION,
        }

    @property
    def is_fatal(self) -> bool:
        """致命的なエラーかどうかを判定"""
        return self in {
            ErrorResult.FAIL,
            ErrorResult.EXPIRED,
            ErrorResult.ACCOUNT_LOCKED,
        }


class BrowserErrorController(ModuleBase):
    selectors: Selector
    RESTART_COUNT = 3
    MAX_RETRY = 3
    RETRY_WAIT_SECONDS = 2
    TIMEOUT_SECONDS = 10
    # エラーメッセージのパターン
    ERROR_PATTERNS = {
        ErrorResult.RECAPTCHA: [
            "ボット",
            "自動化",
            "不正なアクセス",
            "ReCAPTCHA",
            "画像認証",
            "文字認証",
            "認証コード",
        ],
        ErrorResult.INVALID_CREDENTIALS: [
            "ユーザーID",
            "パスワード",
            "正しくありません",
            "認証に失敗",
        ],
        ErrorResult.EXPIRED: ["有効期限", "期限切れ", "セッション", "タイムアウト"],
        ErrorResult.MAINTENANCE: [
            "メンテナンス",
            "システム停止",
            "一時的に利用できません",
        ],
        ErrorResult.NETWORK_ERROR: ["ネットワーク", "接続エラー", "通信に失敗"],
        ErrorResult.ACCOUNT_LOCKED: [
            "アカウントロック",
            "ロックされています",
            "一時停止",
        ],
    }

    def login(self, account) -> ErrorResult:
        error_message = self.browser.get_element_by_css(
            self.selectors.LOGIN_ERROR_MESSAGE
        )
        if not error_message:
            return ErrorResult.SUCCESS
        error_type = self._classify_error(error_message)
        match error_type:
            case "bot":
                return self._handle_bot_error(account)
            case "incorrect":
                return self._handle_incorrect_credentials(account)
            case "expired":
                return self._handle_expired_session(account)
            case "maintenance":
                return self._handle_maintenance_error()
            case "network":
                return self._handle_network_error()
            case "locked":
                return self._handle_account_locked(account)
            case "captcha":
                return self._handle_captcha_required(account)
            case _:
                return self._handle_unknown_error(error_message)
        return ErrorResult.FAIL

    def _classify_error(self, error_message: WebElement):
        error_message_lower = error_message.text.lower()
        for error_type, patterns in self.ERROR_PATTERNS.items():
            if any(pattern in error_message_lower for pattern in patterns):
                return error_type

        return "unknown"

    def _handle_bot_error(self, account: M_Account) -> ErrorResult:
        """ボット検出エラーの処理"""
        self.logger.warning("ボット検出エラー - ReCAPTCHA処理が必要")

        # ログインフォームを再送信
        self.site.auth.send_login_form(account)

        # ユーザーにReCAPTCHA処理を要求
        input("ReCAPTCHA を解決してマイページに移動したら Enter を押してください...")

        # マイページに移動できたかチェック
        if self.site.is_logged_in():
            self.logger.info("ReCAPTCHA処理完了")
            return ErrorResult.SUCCESS
        else:
            self.logger.error("ReCAPTCHA処理後もログインできていません")
            return ErrorResult.RECAPTCHA

    def _handle_incorrect_credentials(self, account: M_Account) -> ErrorResult:
        """認証情報エラーの処理"""
        self.logger.error(f"認証情報が正しくありません: {account.name}")
        self.logger.error("アカウント情報を確認してください")
        return ErrorResult.FAIL

    def _handle_expired_session(self, account: M_Account) -> ErrorResult:
        """セッション期限切れエラーの処理"""
        self.logger.warning("セッションが期限切れです - 再ログインを試行")

        # トップページに戻る
        self.site.go_to_top()
        time.sleep(1)

        # 再ログイン
        if self.site.auth.login(account):
            self.logger.info("再ログイン成功")
            return ErrorResult.SUCCESS
        else:
            self.logger.error("再ログイン失敗")
            return ErrorResult.EXPIRED

    def _handle_maintenance_error(self) -> ErrorResult:
        """メンテナンスエラーの処理"""
        self.logger.warning("システムメンテナンス中です")
        return ErrorResult.MAINTENANCE

    def _handle_network_error(self) -> ErrorResult:
        """ネットワークエラーの処理"""
        self.logger.warning("ネットワークエラーが発生しました")
        time.sleep(self.retry_delay)
        return ErrorResult.NETWORK_ERROR

    def _handle_account_locked(self, account: M_Account) -> ErrorResult:
        """アカウントロックエラーの処理"""
        self.logger.error(f"アカウントがロックされています: {account.name}")
        return ErrorResult.ACCOUNT_LOCKED

    def _handle_captcha_required(self, account: M_Account) -> ErrorResult:
        """CAPTCHA要求エラーの処理"""
        self.logger.warning("CAPTCHA認証が必要です")
        input("CAPTCHA認証を完了してから Enter を押してください...")
        return ErrorResult.SUCCESS

    def _handle_unknown_error(self, error_message: str) -> ErrorResult:
        """未知のエラーの処理"""
        self.logger.error(f"未処理のエラー: {error_message}")
        return ErrorResult.UNKNOWN
