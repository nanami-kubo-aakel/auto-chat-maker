"""
Azure AD認証設定管理モジュール
"""
from typing import Optional

from pydantic_settings import BaseSettings


class AzureSettings(BaseSettings):
    """Azure AD認証設定クラス"""

    # Azure AD基本設定
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None

    # 認証エンドポイント
    authority: str = "https://login.microsoftonline.com"
    redirect_uri: str = "http://localhost:8000/auth/callback"

    # スコープ設定
    scopes: str = "Chat.ReadWrite,User.Read"

    # トークン設定
    token_cache_file: str = ".token_cache.json"
    token_expiration_buffer: int = 300  # 5分

    # セッション設定
    session_secret: Optional[str] = None
    session_timeout: int = 3600  # 1時間

    # セキュリティ設定
    enable_https: bool = False
    allowed_hosts: str = "localhost,127.0.0.1"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"
        env_prefix = "AZURE_"


azure_settings = AzureSettings()


def get_azure_settings() -> AzureSettings:
    """Azure AD設定インスタンスを取得"""
    return azure_settings
