"""
グローバルエラーハンドラーミドルウェア
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from auto_chat_maker.utils.exceptions import AutoChatMakerException
from auto_chat_maker.utils.logger import get_logger

logger = get_logger(__name__)


async def auto_chat_maker_exception_handler(
    request: Request, exc: AutoChatMakerException
) -> JSONResponse:
    """Auto Chat Maker例外のハンドラー"""
    logger.error(
        "Auto Chat Maker例外が発生",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": exc.error_code or "INTERNAL_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """バリデーション例外のハンドラー"""
    logger.error(
        "バリデーションエラーが発生",
        errors=exc.errors(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "リクエストのバリデーションに失敗しました",
                "details": exc.errors(),
            }
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """HTTP例外のハンドラー"""
    logger.error(
        "HTTP例外が発生",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
            }
        },
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """一般的な例外のハンドラー"""
    logger.error(
        "予期しない例外が発生",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "内部サーバーエラーが発生しました",
            }
        },
    )
