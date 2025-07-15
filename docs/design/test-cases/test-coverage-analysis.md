# テストカバレッジ分析

## 概要

Auto Chat Makerプロジェクトのテストカバレッジの詳細分析を説明します。

## 全体カバレッジ状況

**全体カバレッジ: 36% (226/352行)**

### カバレッジ詳細

| ファイル | ステートメント | 未カバー | カバレッジ | 状況 |
|---------|---------------|---------|-----------|------|
| `src/auto_chat_maker/__init__.py` | 5 | 0 | 100% | ✅ 完了 |
| `src/auto_chat_maker/config/settings.py` | 55 | 0 | 100% | ✅ 完了 |
| `src/auto_chat_maker/utils/exceptions.py` | 33 | 0 | 100% | ✅ 完了 |
| `src/auto_chat_maker/utils/logger.py` | 30 | 1 | 97% | ⚠️ ほぼ完了 |
| `src/auto_chat_maker/main.py` | 38 | 38 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/api/routes/health.py` | 19 | 19 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/api/middleware/error_handler.py` | 25 | 25 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/domain/models/user.py` | 15 | 15 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/domain/models/chat_message.py` | 26 | 26 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/domain/models/reply_suggestion.py` | 24 | 24 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/domain/models/subscription.py` | 26 | 26 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/config/azure_settings.py` | 23 | 23 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/config/mcp_settings.py` | 24 | 24 | 0% | ❌ 未実装 |
| `src/auto_chat_maker/domain/repositories/interfaces.py` | 5 | 5 | 0% | ❌ 未実装 |

## レイヤー別カバレッジ分析

### 1. 設定管理レイヤー (config)

**カバレッジ: 67% (102/153行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| `settings.py` | 100% | ✅ 完了 |
| `azure_settings.py` | 0% | ❌ 未実装 |
| `mcp_settings.py` | 0% | ❌ 未実装 |

**改善計画**:
- `azure_settings.py`のテスト実装
- `mcp_settings.py`のテスト実装

### 2. ユーティリティレイヤー (utils)

**カバレッジ: 97% (63/65行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| `exceptions.py` | 100% | ✅ 完了 |
| `logger.py` | 97% | ⚠️ ほぼ完了 |

**改善計画**:
- `logger.py`の残り1行のカバレッジ

### 3. APIレイヤー (api)

**カバレッジ: 0% (0/44行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| `routes/health.py` | 0% | ❌ 未実装 |
| `middleware/error_handler.py` | 0% | ❌ 未実装 |

**改善計画**:
- ヘルスチェックエンドポイントのテスト実装
- エラーハンドラーのテスト実装

### 4. ドメインレイヤー (domain)

**カバレッジ: 0% (0/72行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| `models/user.py` | 0% | ❌ 未実装 |
| `models/chat_message.py` | 0% | ❌ 未実装 |
| `models/reply_suggestion.py` | 0% | ❌ 未実装 |
| `models/subscription.py` | 0% | ❌ 未実装 |
| `repositories/interfaces.py` | 0% | ❌ 未実装 |

**改善計画**:
- 全エンティティのテスト実装
- リポジトリインターフェースのテスト実装

### 5. アプリケーション層 (application)

**カバレッジ: 0% (0/0行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| 未実装 | - | ❌ 未実装 |

**改善計画**:
- ユースケースのテスト実装
- スケジューラーのテスト実装

### 6. インフラ層 (infrastructure)

**カバレッジ: 0% (0/0行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| 未実装 | - | ❌ 未実装 |

**改善計画**:
- データベース実装のテスト
- 外部API実装のテスト

### 7. サービス層 (services)

**カバレッジ: 0% (0/0行)**

| ファイル | カバレッジ | 状況 |
|---------|-----------|------|
| 未実装 | - | ❌ 未実装 |

**改善計画**:
- ビジネスロジックのテスト実装

## 未カバー行の詳細分析

### 1. utils/logger.py (1行未カバー)

**未カバー行**: 69行目
```python
def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
```

**原因**: この関数に対するテストケースが未実装

**解決策**:
```python
def test_configure_logging():
    """configure_logging関数のテスト"""
    # Arrange
    original_logger = logger_config

    # Act
    configure_logging("DEBUG", "console")

    # Assert
    assert logger_config.log_level == "DEBUG"
    assert logger_config.log_format == "console"

    # Cleanup
    global logger_config
    logger_config = original_logger
```

### 2. main.py (38行未カバー)

**未カバー行**: 4-101行
**原因**: アプリケーションエントリーポイントのテストが未実装

**必要なテストケース**:
```python
def test_create_app():
    """create_app関数のテスト"""

def test_lifespan():
    """lifespan関数のテスト"""

def test_root_endpoint():
    """ルートエンドポイントのテスト"""
```

### 3. API層 (44行未カバー)

**未カバー行**:
- `routes/health.py`: 4-62行
- `middleware/error_handler.py`: 5-99行

**必要なテストケース**:
```python
# ヘルスチェックテスト
def test_health_check_endpoint():
    """ヘルスチェックエンドポイントのテスト"""

def test_detailed_health_check_endpoint():
    """詳細ヘルスチェックエンドポイントのテスト"""

# エラーハンドラーテスト
def test_auto_chat_maker_exception_handler():
    """AutoChatMakerExceptionハンドラーのテスト"""

def test_validation_exception_handler():
    """バリデーション例外ハンドラーのテスト"""
```

### 4. ドメイン層 (72行未カバー)

**未カバー行**: 全エンティティとインターフェース

**必要なテストケース**:
```python
# エンティティテスト
def test_user_entity():
    """ユーザーエンティティのテスト"""

def test_chat_message_entity():
    """チャットメッセージエンティティのテスト"""

def test_reply_suggestion_entity():
    """返信案エンティティのテスト"""

def test_subscription_entity():
    """サブスクリプションエンティティのテスト"""
```

## カバレッジ改善計画

### Phase 1: 高優先度 (1-2週間)

1. **API層テスト実装**
   - ヘルスチェックエンドポイント
   - エラーハンドラー
   - 目標カバレッジ: 80%

2. **ドメイン層テスト実装**
   - 全エンティティのテスト
   - リポジトリインターフェース
   - 目標カバレッジ: 80%

3. **ユーティリティテスト完了**
   - logger.pyの残り1行
   - 目標カバレッジ: 100%

### Phase 2: 中優先度 (2-4週間)

1. **設定クラステスト実装**
   - azure_settings.py
   - mcp_settings.py
   - 目標カバレッジ: 100%

2. **アプリケーション層テスト実装**
   - ユースケース
   - スケジューラー
   - 目標カバレッジ: 80%

### Phase 3: 低優先度 (4-8週間)

1. **インフラ層テスト実装**
   - データベース実装
   - 外部API実装
   - 目標カバレッジ: 80%

2. **サービス層テスト実装**
   - ビジネスロジック
   - 目標カバレッジ: 80%

## カバレッジ測定方法

### 実行コマンド

```bash
# 全体カバレッジ測定
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# 特定モジュールのカバレッジ測定
pytest tests/unit/config/ --cov=src/auto_chat_maker/config --cov-report=term-missing

# カバレッジレポート生成
pytest tests/ --cov=src --cov-report=html
```

### カバレッジレポート

HTMLレポートは `htmlcov/` ディレクトリに生成されます。

## 品質基準

### 目標カバレッジ

- **全体カバレッジ**: 80%以上
- **重要モジュール**: 90%以上
- **ユーティリティ**: 100%

### 除外対象

- 設定ファイル (`__init__.py`)
- 型ヒントのみのファイル
- 外部ライブラリのコード

## 関連ドキュメント

- [テストケース概要](./test-case-overview.md)
- [単体テストケース詳細](./unit-test-cases.md)
- [テスト実装計画](./test-implementation-plan.md)
