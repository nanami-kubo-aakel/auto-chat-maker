# 単体テストケース詳細

## 概要

Auto Chat Makerプロジェクトの単体テストケースの詳細を説明します。

## 実装済みテストケース

### 1. 設定管理テスト (config/settings)

**ファイル**: `tests/unit/config/test_settings.py`
**テストケース数**: 12
**カバレッジ**: 100%

#### TestSettings クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_settings_default_values` | デフォルト値の設定 | 全デフォルト値が正しく設定される |
| `test_settings_environment_variables` | 環境変数の読み込み | 環境変数が正しく読み込まれる |
| `test_settings_azure_config` | Azure AD設定 | Azure AD設定が正しく読み込まれる |
| `test_settings_claude_config` | Claude API設定 | Claude API設定が正しく読み込まれる |
| `test_settings_mcp_config` | MCPサーバー設定 | MCPサーバー設定が正しく読み込まれる |
| `test_settings_webhook_config` | Webhook設定 | Webhook設定が正しく読み込まれる |
| `test_settings_reply_generation_config` | 返信生成設定 | 返信生成設定が正しく読み込まれる |
| `test_settings_feature_flags` | 機能フラグ | 機能フラグが正しく読み込まれる |
| `test_settings_optional_fields` | オプションフィールド | 空文字列がNoneに変換される |
| `test_settings_case_insensitive` | 大文字小文字区別 | 環境変数名が大文字小文字を区別しない |

#### TestGetSettings クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_get_settings_returns_singleton` | シングルトンパターン | 同じインスタンスが返される |
| `test_get_settings_returns_settings_instance` | 戻り値の型 | Settingsインスタンスが返される |

### 2. 例外処理テスト (utils/exceptions)

**ファイル**: `tests/unit/utils/test_exceptions.py`
**テストケース数**: 12
**カバレッジ**: 100%

#### TestAutoChatMakerException クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_exception_creation_with_message` | メッセージのみでの例外作成 | メッセージが正しく設定される |
| `test_exception_creation_with_message_and_error_code` | メッセージとエラーコードでの例外作成 | メッセージとエラーコードが正しく設定される |
| `test_exception_inheritance` | 継承関係 | Exceptionクラスを継承している |

#### TestConfigurationError クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_configuration_error_inheritance` | 継承関係 | AutoChatMakerExceptionを継承している |
| `test_configuration_error_message` | メッセージ設定 | 設定エラーのメッセージが正しく設定される |

#### TestMCPConnectionError クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_mcp_connection_error_inheritance` | 継承関係 | AutoChatMakerExceptionを継承している |
| `test_mcp_connection_error_with_error_code` | エラーコード設定 | MCP接続エラーにエラーコードを設定できる |

#### TestAuthenticationError クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_authentication_error_inheritance` | 継承関係 | AutoChatMakerExceptionを継承している |
| `test_authentication_error_message` | メッセージ設定 | 認証エラーのメッセージが正しく設定される |

#### TestValidationError クラス

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_validation_error_inheritance` | 継承関係 | AutoChatMakerExceptionを継承している |
| `test_validation_error_with_error_code` | エラーコード設定 | バリデーションエラーにエラーコードを設定できる |
| `test_validation_error_str_representation` | 文字列表現 | バリデーションエラーの文字列表現が正しい |

### 3. ログ機能テスト (utils/logger)

**ファイル**: `tests/unit/utils/test_logger.py`
**テストケース数**: 4
**カバレッジ**: 97%

#### LoggerConfig テスト

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_logger_config_setup_logging` | ログ設定初期化 | loggingとstructlogが初期化される |

#### AppLogger テスト

| テストメソッド | テスト内容 | 期待される結果 |
|---------------|-----------|---------------|
| `test_app_logger_info_logs_message` | 情報ログ出力 | 情報ログが正しく出力される |
| `test_app_logger_error_logs_message` | エラーログ出力 | エラーログが正しく出力される |
| `test_app_logger_debug_logs_message` | デバッグログ出力 | デバッグログが正しく出力される |

## テスト実装パターン

### TDD (Test-Driven Development) アプローチ

実装済みテストは、t-wada氏のTDDの考え方に基づいて実装されています：

1. **Red**: 失敗するテストを書く
2. **Green**: テストが通る最小限の実装
3. **Refactor**: コードの改善

### テスト設計原則

1. **独立性**: 各テストは独立して実行可能
2. **明確性**: テスト名と内容が明確
3. **網羅性**: 正常系・異常系を網羅
4. **保守性**: テストコードも保守しやすい構造

### モック・スタブの使用

- `monkeypatch`: 外部依存をモック化
- `caplog`: ログ出力のテスト
- `patch.dict`: 環境変数のモック化

## 未実装テストケース

### 1. API層テスト

#### ルーター・コントローラーテスト

| 対象ファイル | テスト内容 | 優先度 |
|-------------|-----------|--------|
| `api/routes/health.py` | ヘルスチェックエンドポイント | 高 |
| `api/middleware/error_handler.py` | エラーハンドラー | 高 |

#### 必要なテストケース

```python
# ヘルスチェックテスト例
def test_health_check_returns_200():
    """ヘルスチェックが200を返すことをテスト"""

def test_health_check_returns_correct_data():
    """ヘルスチェックが正しいデータを返すことをテスト"""

def test_detailed_health_check_returns_components():
    """詳細ヘルスチェックがコンポーネント情報を返すことをテスト"""
```

### 2. ドメイン層テスト

#### エンティティテスト

| 対象ファイル | テスト内容 | 優先度 |
|-------------|-----------|--------|
| `domain/models/user.py` | ユーザーエンティティ | 高 |
| `domain/models/chat_message.py` | チャットメッセージエンティティ | 高 |
| `domain/models/reply_suggestion.py` | 返信案エンティティ | 高 |
| `domain/models/subscription.py` | サブスクリプションエンティティ | 中 |

#### 必要なテストケース

```python
# ユーザーエンティティテスト例
def test_user_creation():
    """ユーザー作成をテスト"""

def test_user_str_representation():
    """ユーザーの文字列表現をテスト"""

def test_user_validation():
    """ユーザーのバリデーションをテスト"""
```

### 3. 設定クラステスト

#### 追加設定テスト

| 対象ファイル | テスト内容 | 優先度 |
|-------------|-----------|--------|
| `config/azure_settings.py` | Azure設定クラス | 中 |
| `config/mcp_settings.py` | MCP設定クラス | 中 |

## テスト実行方法

### 個別テスト実行

```bash
# 設定テストのみ実行
pytest tests/unit/config/test_settings.py -v

# 例外テストのみ実行
pytest tests/unit/utils/test_exceptions.py -v

# ログテストのみ実行
pytest tests/unit/utils/test_logger.py -v
```

### カバレッジ付き実行

```bash
# 特定モジュールのカバレッジ確認
pytest tests/unit/config/ --cov=src/auto_chat_maker/config --cov-report=term-missing

# 全単体テストのカバレッジ確認
pytest tests/unit/ --cov=src --cov-report=html
```

## 品質指標

### 現在の状況

- ✅ **テスト成功率**: 100% (28/28)
- ✅ **テスト実行時間**: 0.82秒
- ⚠️ **カバレッジ**: 36% (改善必要)
- ❌ **未実装テスト**: 多数

### 目標

- **カバレッジ**: 80%以上
- **テスト実行時間**: 5分以内
- **テスト成功率**: 100%
- **テスト独立性**: 100%

## 関連ドキュメント

- [テストケース概要](./test-case-overview.md)
- [テストカバレッジ分析](./test-coverage-analysis.md)
- [テスト実装計画](./test-implementation-plan.md)
