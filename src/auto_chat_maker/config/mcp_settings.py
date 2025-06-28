"""
MCPサーバー設定管理モジュール
"""
from typing import Optional

from pydantic_settings import BaseSettings


class MCPSettings(BaseSettings):
    """MCPサーバー設定クラス"""

    # MCPサーバー基本設定
    server_url: Optional[str] = None
    api_key: Optional[str] = None

    # サーバー情報
    server_name: str = "ms-365-mcp-server"
    server_version: str = "1.0.0"
    server_description: str = "Microsoft 365 MCP Server"

    # 接続設定
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1

    # 認証設定
    auth_type: str = "oauth2"
    token_endpoint: Optional[str] = None

    # 機能設定
    enable_chat_operations: bool = True
    enable_mail_operations: bool = False
    enable_calendar_operations: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"
        env_prefix = "MCP_"


mcp_settings = MCPSettings()


def get_mcp_settings() -> MCPSettings:
    """MCP設定インスタンスを取得"""
    return mcp_settings
