"""
Auto Chat Maker メインアプリケーション
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from auto_chat_maker.api.middleware.error_handler import (
    auto_chat_maker_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from auto_chat_maker.config.settings import get_settings
from auto_chat_maker.utils.exceptions import AutoChatMakerException
from auto_chat_maker.utils.logger import get_logger

# ロガーの初期化
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    logger.info("アプリケーションを起動中...")
    settings = get_settings()
    logger.info(f"アプリケーション名: {settings.app_name}")
    logger.info(f"バージョン: {settings.app_version}")
    logger.info(f"デバッグモード: {settings.debug}")

    yield

    # 終了時の処理
    logger.info("アプリケーションを終了中...")


def create_app() -> FastAPI:
    """FastAPIアプリケーションを作成"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Microsoft Teamsチャット自動返信システム",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 開発環境用
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # エラーハンドラーの登録
    app.add_exception_handler(
        AutoChatMakerException, auto_chat_maker_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # ルーティングの登録
    from auto_chat_maker.api.routes.health import router as health_router

    app.include_router(health_router, prefix="/api")

    # 他のルーティングは後で実装
    # from auto_chat_maker.api.routes import auth, webhook, ui, chat
    # app.include_router(auth.router, prefix="/api/auth")
    # app.include_router(webhook.router, prefix="/api/webhook")
    # app.include_router(ui.router, prefix="/ui")
    # app.include_router(chat.router, prefix="/api/chat")

    return app


# アプリケーションインスタンス
app = create_app()


@app.get("/")  # type: ignore[misc]
async def root() -> dict:
    """ルートエンドポイント"""
    return {"message": "Auto Chat Maker API", "version": "1.0.0"}


@app.get("/health")  # type: ignore[misc]
async def health_check() -> dict:
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "Auto Chat Maker"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "auto_chat_maker.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
