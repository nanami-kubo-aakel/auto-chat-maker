"""
環境変数・.envファイルから設定値を読み込む参照用モジュール
"""
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション全体の設定値を環境変数から読み込むクラス"""

    # アプリケーション基本設定
    app_name: Optional[str] = None
    app_version: Optional[str] = None
    debug: Optional[bool] = None
    log_level: Optional[str] = None
    secret_key: Optional[str] = None

    # データベース設定
    database_url: Optional[str] = None
    redis_url: Optional[str] = None

    # Azure AD認証設定
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    azure_ad_authority: Optional[str] = None
    azure_ad_scopes: Optional[str] = None

    # Claude API設定
    claude_api_key: Optional[str] = None
    claude_api_base_url: Optional[str] = "https://api.anthropic.com"
    claude_model: Optional[str] = "claude-3-sonnet-20240229"
    claude_max_tokens: Optional[int] = 4000
    claude_temperature: Optional[float] = 0.7

    # MCPサーバー設定
    mcp_server_url: Optional[str] = None
    mcp_api_key: Optional[str] = None
    mcp_server_name: Optional[str] = None
    mcp_server_version: Optional[str] = None
    mcp_server_description: Optional[str] = None
    mcp_connection_timeout: Optional[int] = 30
    mcp_max_retries: Optional[int] = 3

    # Webhook設定
    webhook_secret: Optional[str] = None
    webhook_endpoint: Optional[str] = "/webhook"
    webhook_timeout: Optional[int] = 10

    # 返信生成設定
    reply_generation_batch_size: Optional[int] = 10
    reply_generation_interval: Optional[int] = 300  # 5分
    reply_quality_threshold: Optional[float] = 0.8

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


settings = Settings()


def get_settings() -> Settings:
    """設定インスタンスを取得"""
    return settings
