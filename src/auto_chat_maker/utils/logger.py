"""
ログ設定管理モジュール
"""
import logging
import sys

import structlog
from structlog.stdlib import LoggerFactory


class LoggerConfig:
    """ログ設定クラス"""

    def __init__(self, log_level: str = "INFO", log_format: str = "json"):
        self.log_level = log_level
        self.log_format = log_format
        self._configure_logging()

    def _configure_logging(self) -> None:
        """ログ設定を初期化"""
        # structlogの設定
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
                if self.log_format == "json"
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # 標準ライブラリのログレベル設定
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, self.log_level.upper()),
        )

    def get_logger(self, name: str) -> structlog.stdlib.BoundLogger:
        """ロガーを取得"""
        return structlog.get_logger(name)


# デフォルトロガー設定
logger_config = LoggerConfig()
get_logger = logger_config.get_logger


def configure_logging(
    log_level: str = "INFO", log_format: str = "json"
) -> None:
    """ログ設定を更新"""
    global logger_config
    logger_config = LoggerConfig(log_level, log_format)
