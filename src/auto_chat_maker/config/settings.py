"""
環境変数・.envファイルから設定値を読み込む参照用モジュール
"""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """アプリケーション全体の設定値を環境変数から読み込むクラス"""
    # ここではデフォルト値や機密値は記載しません
    app_name: Optional[str] = None
    app_version: Optional[str] = None
    debug: Optional[bool] = None
    log_level: Optional[str] = None
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    claude_api_key: Optional[str] = None
    mcp_server_url: Optional[str] = None
    mcp_api_key: Optional[str] = None
    secret_key: Optional[str] = None
    webhook_secret: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"

settings = Settings()

def get_settings() -> Settings:
    """設定インスタンスを取得"""
    return settings 