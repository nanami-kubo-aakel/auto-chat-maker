"""
カスタム例外クラスのテスト

t-wada氏のTDDの考え方に基づいて実装:
1. Red: 失敗するテストを書く
2. Green: テストが通る最小限の実装
3. Refactor: コードの改善
"""


from auto_chat_maker.utils.exceptions import (
    AuthenticationError,
    AutoChatMakerException,
    ConfigurationError,
    MCPConnectionError,
    ValidationError,
)


class TestAutoChatMakerException:
    """AutoChatMakerExceptionのテスト"""

    def test_exception_creation_with_message(self) -> None:
        """メッセージのみで例外を作成できることをテスト"""
        # Arrange
        message = "テストエラーメッセージ"

        # Act
        exception = AutoChatMakerException(message)

        # Assert
        assert exception.message == message
        assert exception.error_code is None
        assert str(exception) == message

    def test_exception_creation_with_message_and_error_code(self) -> None:
        """メッセージとエラーコードで例外を作成できることをテスト"""
        # Arrange
        message = "テストエラーメッセージ"
        error_code = "TEST_ERROR_001"

        # Act
        exception = AutoChatMakerException(message, error_code)

        # Assert
        assert exception.message == message
        assert exception.error_code == error_code
        assert str(exception) == message

    def test_exception_inheritance(self) -> None:
        """Exceptionクラスを継承していることをテスト"""
        # Arrange & Act
        exception = AutoChatMakerException("テスト")

        # Assert
        assert isinstance(exception, Exception)


class TestConfigurationError:
    """ConfigurationErrorのテスト"""

    def test_configuration_error_inheritance(self) -> None:
        """AutoChatMakerExceptionを継承していることをテスト"""
        # Arrange & Act
        exception = ConfigurationError("設定エラー")

        # Assert
        assert isinstance(exception, AutoChatMakerException)
        assert isinstance(exception, Exception)

    def test_configuration_error_message(self) -> None:
        """設定エラーのメッセージが正しく設定されることをテスト"""
        # Arrange
        message = "設定ファイルが見つかりません"

        # Act
        exception = ConfigurationError(message)

        # Assert
        assert exception.message == message
        assert str(exception) == message


class TestMCPConnectionError:
    """MCPConnectionErrorのテスト"""

    def test_mcp_connection_error_inheritance(self) -> None:
        """AutoChatMakerExceptionを継承していることをテスト"""
        # Arrange & Act
        exception = MCPConnectionError("MCP接続エラー")

        # Assert
        assert isinstance(exception, AutoChatMakerException)
        assert isinstance(exception, Exception)

    def test_mcp_connection_error_with_error_code(self) -> None:
        """MCP接続エラーにエラーコードを設定できることをテスト"""
        # Arrange
        message = "MCPサーバーに接続できません"
        error_code = "MCP_CONNECTION_FAILED"

        # Act
        exception = MCPConnectionError(message, error_code)

        # Assert
        assert exception.message == message
        assert exception.error_code == error_code


class TestAuthenticationError:
    """AuthenticationErrorのテスト"""

    def test_authentication_error_inheritance(self) -> None:
        """AutoChatMakerExceptionを継承していることをテスト"""
        # Arrange & Act
        exception = AuthenticationError("認証エラー")

        # Assert
        assert isinstance(exception, AutoChatMakerException)
        assert isinstance(exception, Exception)

    def test_authentication_error_message(self) -> None:
        """認証エラーのメッセージが正しく設定されることをテスト"""
        # Arrange
        message = "認証トークンが無効です"

        # Act
        exception = AuthenticationError(message)

        # Assert
        assert exception.message == message
        assert str(exception) == message


class TestValidationError:
    """ValidationErrorのテスト"""

    def test_validation_error_inheritance(self) -> None:
        """AutoChatMakerExceptionを継承していることをテスト"""
        # Arrange & Act
        exception = ValidationError("バリデーションエラー")

        # Assert
        assert isinstance(exception, AutoChatMakerException)
        assert isinstance(exception, Exception)

    def test_validation_error_with_error_code(self) -> None:
        """バリデーションエラーにエラーコードを設定できることをテスト"""
        # Arrange
        message = "入力データが不正です"
        error_code = "VALIDATION_FAILED"

        # Act
        exception = ValidationError(message, error_code)

        # Assert
        assert exception.message == message
        assert exception.error_code == error_code

    def test_validation_error_str_representation(self) -> None:
        """バリデーションエラーの文字列表現をテスト"""
        # Arrange
        message = "必須フィールドが不足しています"

        # Act
        exception = ValidationError(message)

        # Assert
        assert str(exception) == message
        assert repr(exception) == f"ValidationError('{message}')"
