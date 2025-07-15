"""
環境変数・.envファイルから設定値を読み込む参照用モジュール
"""
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション全体の設定値を環境変数から読み込むクラス"""

    # アプリケーション基本設定
    app_name: str = "Auto Chat Maker"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: Optional[str] = None
    host: str = "0.0.0.0"
    port: int = 8000

    # データベース設定
    database_url: str = "sqlite:///./auto_chat_maker.db"
    database_echo: bool = False

    # Azure AD認証設定
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    azure_ad_authority: str = "https://login.microsoftonline.com"
    azure_ad_scopes: str = "Chat.ReadWrite,User.Read"

    # Claude API設定
    claude_api_key: Optional[str] = None
    claude_api_base_url: str = "https://api.anthropic.com"
    claude_model: str = "claude-3-sonnet-20240229"
    claude_max_tokens: int = 4000
    claude_temperature: float = 0.7

    # MCPサーバー設定
    mcp_server_url: Optional[str] = None
    mcp_api_key: Optional[str] = None
    mcp_server_name: str = "ms-365-mcp-server"
    mcp_server_version: str = "1.0.0"
    mcp_server_description: str = "Microsoft 365 MCP Server"
    mcp_connection_timeout: int = 30
    mcp_max_retries: int = 3

    # Webhook設定
    webhook_secret: Optional[str] = None
    webhook_endpoint: str = "/api/webhook/microsoft-graph"
    webhook_timeout: int = 10
    webhook_subscription_expiration: int = 3600  # 60分

    # 返信生成設定
    reply_generation_batch_size: int = 10
    reply_generation_interval: int = 300  # 5分
    reply_quality_threshold: float = 0.8
    max_reply_suggestions: int = 3

    # 機能フラグ
    enable_teams_plugin: bool = True
    enable_mail_plugin: bool = False
    enable_ai_processing: bool = True
    enable_webhook_processing: bool = True

    @field_validator(
        "secret_key",
        "microsoft_client_id",
        "microsoft_client_secret",
        "microsoft_tenant_id",
        "claude_api_key",
        "mcp_server_url",
        "mcp_api_key",
        "webhook_secret",
        mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


settings = Settings()


def get_settings() -> Settings:
    """設定インスタンスを取得"""
    return settings
