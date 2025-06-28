"""
カスタム例外クラス定義モジュール
"""
from typing import Any, Dict, Optional


class AutoChatMakerException(Exception):
    """Auto Chat Makerシステムの基底例外クラス"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(AutoChatMakerException):
    """設定エラー"""

    pass


class AuthenticationError(AutoChatMakerException):
    """認証エラー"""

    pass


class AuthorizationError(AutoChatMakerException):
    """認可エラー"""

    pass


class MCPConnectionError(AutoChatMakerException):
    """MCPサーバー接続エラー"""

    pass


class MCPOperationError(AutoChatMakerException):
    """MCP操作エラー"""

    pass


class WebhookError(AutoChatMakerException):
    """Webhook処理エラー"""

    pass


class AIProcessingError(AutoChatMakerException):
    """AI処理エラー"""

    pass


class DatabaseError(AutoChatMakerException):
    """データベースエラー"""

    pass


class ValidationError(AutoChatMakerException):
    """バリデーションエラー"""

    pass


class ExternalServiceError(AutoChatMakerException):
    """外部サービスエラー"""

    pass


class RateLimitError(ExternalServiceError):
    """レート制限エラー"""

    pass


class TimeoutError(ExternalServiceError):
    """タイムアウトエラー"""

    pass


class NetworkError(ExternalServiceError):
    """ネットワークエラー"""

    pass
