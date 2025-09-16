from __future__ import annotations

import time
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from database import M_Account

if TYPE_CHECKING:
    from .site import NetAichi
from utils import AppLogger


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


class Selector:
    LOGIN_ERROR_MESSAGE = "#allMessages2"
    GENERAL_ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    WARNING_MESSAGE = ".warning-message"


class ErrorHandler:
    logger = AppLogger("ErrorHandler")
    """エラーハンドリングを行うクラス"""
    selectors: Selector = Selector()
    site: NetAichi
    # エラーメッセージのパターン
    ERROR_PATTERNS = {
        ErrorResult.RECAPTCHA: ["不正な操作によりログイン処理に失敗しました。"],
        ErrorResult.INVALID_CREDENTIALS: [
            "利用者番号",
            "パスワード",
            "誤っています",
        ],
        ErrorResult.EXPIRED: ["アカウントの有効期限が切れています。"],
    }

    def __init__(self, site: NetAichi):
        self.site = site
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 2

    def _get_error_message(self, selector: str) -> Optional[str]:
        """エラーメッセージを取得"""
        element = self.site.browser.get_element_by_css(selector)
        if element and element.text.strip():
            return element.text.strip()
        return None

    def _classify_error(self, error_message: str) -> ErrorResult:
        """エラーメッセージを分類"""
        error_message_lower = error_message.lower()

        for error_type, patterns in self.ERROR_PATTERNS.items():
            if any(pattern in error_message_lower for pattern in patterns):
                return error_type
        self.logger.error(f"未分類のエラーメッセージ: {error_message}")
        return ErrorResult.UNKNOWN

    def login(self) -> ErrorResult:
        """ログインエラーのハンドリング"""
        try:
            error_message = self._get_error_message(self.selectors.LOGIN_ERROR_MESSAGE)
        except NoSuchElementException:
            return ErrorResult.SUCCESS
        if not error_message:
            return ErrorResult.SUCCESS
        self.logger.info(f"ログインエラーメッセージ: {error_message}")
        # エラーメッセージに基づく処理
        error_type = self._classify_error(error_message)
        return error_type

    def lottery(self, error_context: Optional[str] = None) -> ErrorResult:
        """抽選関連のエラーハンドリング"""
        error_message = self._get_error_message() or error_context
        self.logger.info(f"抽選エラーメッセージ: {error_message}")

        if not error_message:
            return ErrorResult.SUCCESS

        # 抽選特有のエラーパターン
        if any(pattern in error_message for pattern in ["締切", "受付終了", "定員"]):
            self.logger.warning("抽選締切またはキャパシティエラー")
            return ErrorResult.FAIL

        if any(pattern in error_message for pattern in ["重複", "既に申込", "申込済"]):
            self.logger.warning("重複申込エラー")
            return ErrorResult.FAIL

        if any(pattern in error_message for pattern in ["ログイン", "セッション"]):
            self.logger.warning("セッションエラー - 再ログインが必要")
            return ErrorResult.INVALID_SESSION

        if any(
            pattern in error_message for pattern in ["一時的", "サーバー", "システム"]
        ):
            self.logger.warning("一時的なシステムエラー")
            return ErrorResult.RETRY

        return self._handle_unknown_error(error_message)

    def reservation(self, error_context: Optional[str] = None) -> ErrorResult:
        """予約関連のエラーハンドリング"""
        error_message = self._get_error_message() or error_context
        self.logger.info(f"予約エラーメッセージ: {error_message}")

        if not error_message:
            return ErrorResult.SUCCESS

        # 予約特有のエラーパターン
        if any(
            pattern in error_message for pattern in ["満席", "予約不可", "空きなし"]
        ):
            self.logger.warning("予約満席エラー")
            return ErrorResult.FAIL

        if any(pattern in error_message for pattern in ["キャンセル不可", "変更不可"]):
            self.logger.warning("予約変更不可エラー")
            return ErrorResult.FAIL

        if any(pattern in error_message for pattern in ["時間外", "営業時間"]):
            self.logger.warning("営業時間外エラー")
            return ErrorResult.FAIL

        if any(pattern in error_message for pattern in ["権限", "アクセス権"]):
            self.logger.warning("権限エラー")
            return ErrorResult.FAIL

        return self._handle_unknown_error(error_message)

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

    def should_retry(self, error_result: ErrorResult) -> bool:
        """リトライすべきかどうかを判定"""
        if self.retry_count >= self.max_retries:
            self.logger.warning(f"最大リトライ回数 ({self.max_retries}) に達しました")
            return False

        if error_result.is_recoverable:
            self.retry_count += 1
            self.logger.info(f"リトライ {self.retry_count}/{self.max_retries}")
            time.sleep(self.retry_delay)
            return True

        return False

    def reset_retry_count(self):
        """リトライカウントをリセット"""
        self.retry_count = 0

    def get_error_summary(self) -> dict:
        """エラー情報のサマリーを取得"""
        return {
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "last_error": getattr(self, "_last_error", None),
            "error_patterns": self.ERROR_PATTERNS,
        }

    def handle_with_retry(self, operation_func, *args, **kwargs):
        """リトライ機能付きでエラーハンドリングを実行

        Returns:
            tuple[bool, ErrorResult]: 成功フラグとエラー結果

        Raises:
            Exception: 操作関数で発生した例外をそのまま再発生
        """
        self.reset_retry_count()

        while True:
            result = operation_func(*args, **kwargs)
            if result == ErrorResult.SUCCESS:
                return True, result

            if not self.should_retry(result):
                return False, result

            self.logger.info(
                f"リトライ実行中... ({self.retry_count}/{self.max_retries})"
            )

    def is_success_page(self) -> bool:
        """成功ページかどうかを判定"""
        success_indicators = [
            self.SUCCESS_MESSAGE,
            ".alert-success",
            ".success",
            "#success-message",
        ]

        for selector in success_indicators:
            element = self.site.browser.get_element_by_css(selector)
            if element and element.text.strip():
                return True

        return False

    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """ページロードを待機

        Raises:
            TimeoutException: タイムアウト時
        """
        self.site.browser.wait_for_element_present("body", timeout=timeout)
        return True
