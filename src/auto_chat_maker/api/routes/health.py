"""
ヘルスチェックエンドポイント
"""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, status

from auto_chat_maker.config.settings import get_settings
from auto_chat_maker.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """ヘルスチェックエンドポイント"""
    settings = get_settings()

    health_info: Dict[str, Any] = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.debug else "production",
    }

    logger.info("ヘルスチェック実行", health_info=health_info)
    return health_info


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """詳細ヘルスチェックエンドポイント"""
    settings = get_settings()

    # 基本的なヘルス情報
    health_info: Dict[str, Any] = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.debug else "production",
        "components": {
            "database": "healthy",  # 後で実装
            "mcp_server": "unknown",  # 後で実装
            "claude_api": "unknown",  # 後で実装
        },
        "settings": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "database_url": settings.database_url,
            "mcp_server_url": settings.mcp_server_url,
            "claude_api_base_url": settings.claude_api_base_url,
        },
    }

    logger.info("詳細ヘルスチェック実行", health_info=health_info)
    return health_info
