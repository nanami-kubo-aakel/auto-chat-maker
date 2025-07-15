"""
Settingsクラスのテスト

t-wada氏のTDDの考え方に基づいて実装:
1. Red: 失敗するテストを書く
2. Green: テストが通る最小限の実装
3. Refactor: コードの改善

.env内の固有の値に依存しないテストを書く
"""

import os
from unittest.mock import patch

import pytest

from auto_chat_maker.config.settings import Settings, get_settings


class TestSettings:
    """Settingsクラスのテスト"""

    def test_settings_default_values(self):
        """デフォルト値が正しく設定されることをテスト"""
        # Arrange & Act
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

        # Assert
        assert settings.app_name == "Auto Chat Maker"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.database_url == "sqlite:///./auto_chat_maker.db"
        assert settings.database_echo is False

    def test_settings_environment_variables(self):
        """環境変数が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "APP_NAME": "Test App",
            "APP_VERSION": "2.0.0",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "DATABASE_URL": "sqlite:///./test.db",
            "DATABASE_ECHO": "true",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.app_name == "Test App"
        assert settings.app_version == "2.0.0"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.database_url == "sqlite:///./test.db"
        assert settings.database_echo is True

    def test_settings_azure_config(self):
        """Azure AD設定が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "MICROSOFT_CLIENT_ID": "test-client-id",
            "MICROSOFT_CLIENT_SECRET": "test-client-secret",
            "MICROSOFT_TENANT_ID": "test-tenant-id",
            "AZURE_AD_AUTHORITY": "https://test.login.microsoftonline.com",
            "AZURE_AD_SCOPES": "Chat.Read,User.Read",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.microsoft_client_id == "test-client-id"
        assert settings.microsoft_client_secret == "test-client-secret"
        assert settings.microsoft_tenant_id == "test-tenant-id"
        assert (
            settings.azure_ad_authority
            == "https://test.login.microsoftonline.com"
        )
        assert settings.azure_ad_scopes == "Chat.Read,User.Read"

    def test_settings_claude_config(self):
        """Claude API設定が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "CLAUDE_API_KEY": "test-claude-key",
            "CLAUDE_API_BASE_URL": "https://test.api.anthropic.com",
            "CLAUDE_MODEL": "claude-3-test",
            "CLAUDE_MAX_TOKENS": "2000",
            "CLAUDE_TEMPERATURE": "0.5",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.claude_api_key == "test-claude-key"
        assert settings.claude_api_base_url == "https://test.api.anthropic.com"
        assert settings.claude_model == "claude-3-test"
        assert settings.claude_max_tokens == 2000
        assert settings.claude_temperature == 0.5

    def test_settings_mcp_config(self):
        """MCPサーバー設定が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "MCP_SERVER_URL": "http://test-mcp-server:3000",
            "MCP_API_KEY": "test-mcp-key",
            "MCP_SERVER_NAME": "test-mcp-server",
            "MCP_SERVER_VERSION": "2.0.0",
            "MCP_CONNECTION_TIMEOUT": "60",
            "MCP_MAX_RETRIES": "5",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.mcp_server_url == "http://test-mcp-server:3000"
        assert settings.mcp_api_key == "test-mcp-key"
        assert settings.mcp_server_name == "test-mcp-server"
        assert settings.mcp_server_version == "2.0.0"
        assert settings.mcp_connection_timeout == 60
        assert settings.mcp_max_retries == 5

    def test_settings_webhook_config(self):
        """Webhook設定が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "WEBHOOK_SECRET": "test-webhook-secret",
            "WEBHOOK_ENDPOINT": "/api/test/webhook",
            "WEBHOOK_TIMEOUT": "20",
            "WEBHOOK_SUBSCRIPTION_EXPIRATION": "7200",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.webhook_secret == "test-webhook-secret"
        assert settings.webhook_endpoint == "/api/test/webhook"
        assert settings.webhook_timeout == 20
        assert settings.webhook_subscription_expiration == 7200

    def test_settings_reply_generation_config(self):
        """返信生成設定が正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "REPLY_GENERATION_BATCH_SIZE": "20",
            "REPLY_GENERATION_INTERVAL": "600",
            "REPLY_QUALITY_THRESHOLD": "0.9",
            "MAX_REPLY_SUGGESTIONS": "5",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.reply_generation_batch_size == 20
        assert settings.reply_generation_interval == 600
        assert settings.reply_quality_threshold == 0.9
        assert settings.max_reply_suggestions == 5

    def test_settings_feature_flags(self):
        """機能フラグが正しく読み込まれることをテスト"""
        # Arrange
        test_env = {
            "ENABLE_TEAMS_PLUGIN": "false",
            "ENABLE_MAIL_PLUGIN": "true",
            "ENABLE_AI_PROCESSING": "false",
            "ENABLE_WEBHOOK_PROCESSING": "true",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.enable_teams_plugin is False
        assert settings.enable_mail_plugin is True
        assert settings.enable_ai_processing is False
        assert settings.enable_webhook_processing is True

    def test_settings_optional_fields(self):
        """オプションフィールドがNoneの場合のテスト"""
        # Arrange
        test_env = {
            "SECRET_KEY": "",
            "MICROSOFT_CLIENT_ID": "",
            "CLAUDE_API_KEY": "",
            "MCP_SERVER_URL": "",
            "WEBHOOK_SECRET": "",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.secret_key is None
        assert settings.microsoft_client_id is None
        assert settings.claude_api_key is None
        assert settings.mcp_server_url is None
        assert settings.webhook_secret is None

    def test_settings_case_insensitive(self):
        """環境変数名が大文字小文字を区別しないことをテスト"""
        # Arrange
        test_env = {
            "app_name": "Test App Case Insensitive",
            "LOG_LEVEL": "WARNING",
        }

        # Act
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

        # Assert
        assert settings.app_name == "Test App Case Insensitive"
        assert settings.log_level == "WARNING"


class TestGetSettings:
    """get_settings関数のテスト"""

    def test_get_settings_returns_singleton(self):
        """get_settingsが同じインスタンスを返すことをテスト"""
        # Act
        settings1 = get_settings()
        settings2 = get_settings()

        # Assert
        assert settings1 is settings2

    def test_get_settings_returns_settings_instance(self):
        """get_settingsがSettingsインスタンスを返すことをテスト"""
        # Act
        settings = get_settings()

        # Assert
        assert isinstance(settings, Settings)
