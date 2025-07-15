"""
LoggerConfig/AppLoggerのテスト

t-wada氏のTDDの考え方に基づいて実装:
1. Red: 失敗するテストを書く
2. Green: テストが通る最小限の実装
3. Refactor: コードの改善
"""

import json
import logging

import structlog

from auto_chat_maker.utils.logger import AppLogger, LoggerConfig


def test_logger_config_setup_logging(monkeypatch) -> None:
    """LoggerConfig.setup_loggingでloggingとstructlogが初期化されること"""
    # Arrange
    config = LoggerConfig(log_level="DEBUG", log_format="json")
    called: dict[str, object] = {}

    def fake_basicConfig(**kwargs: object) -> None:
        called["basicConfig"] = kwargs

    monkeypatch.setattr(logging, "basicConfig", fake_basicConfig)

    def fake_configure(*args: object, **kwargs: object) -> None:
        called["structlog_configure"] = (args, kwargs)

    monkeypatch.setattr(structlog, "configure", fake_configure)

    # Act
    config.setup_logging()

    # Assert
    assert "basicConfig" in called
    assert "structlog_configure" in called


def test_app_logger_info_logs_message(caplog) -> None:
    """AppLogger.infoで情報ログが出力されること"""
    # Arrange
    logger = AppLogger("test_logger")
    message = "infoログテスト"

    # Act
    with caplog.at_level(logging.INFO):
        logger.info(message, user="test")

    # Assert
    # JSONログからeventフィールドを抽出して確認
    log_line = caplog.text.strip()
    json_start = log_line.find("{")
    if json_start != -1:
        json_str = log_line[json_start:]
        log_data = json.loads(json_str)
        assert log_data["event"] == message
        assert log_data["user"] == "test"


def test_app_logger_error_logs_message(caplog) -> None:
    """AppLogger.errorでエラーログが出力されること"""
    # Arrange
    logger = AppLogger("test_logger")
    message = "errorログテスト"

    # Act
    with caplog.at_level(logging.ERROR):
        logger.error(message, error_code="E001")

    # Assert
    # JSONログからeventフィールドを抽出して確認
    log_line = caplog.text.strip()
    json_start = log_line.find("{")
    if json_start != -1:
        json_str = log_line[json_start:]
        log_data = json.loads(json_str)
        assert log_data["event"] == message
        assert log_data["error_code"] == "E001"


def test_app_logger_debug_logs_message(caplog) -> None:
    """AppLogger.debugでデバッグログが出力されること"""
    # Arrange
    logger = AppLogger("test_logger")
    message = "debugログテスト"

    # Act
    with caplog.at_level(logging.DEBUG):
        logger.debug(message, debug_info="test")

    # Assert
    # JSONログからeventフィールドを抽出して確認
    log_line = caplog.text.strip()
    json_start = log_line.find("{")
    if json_start != -1:
        json_str = log_line[json_start:]
        log_data = json.loads(json_str)
        assert log_data["event"] == message
        assert log_data["debug_info"] == "test"
