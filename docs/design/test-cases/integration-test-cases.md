# 統合テストケース詳細

## 概要

Auto Chat Makerプロジェクトの統合テストケースの詳細を説明します。

## 統合テスト戦略

### 統合テストの目的

1. **コンポーネント間の連携確認**
   - 複数のレイヤー間のデータフロー
   - 依存関係の正しい動作確認

2. **外部システムとの統合確認**
   - データベース接続・操作
   - 外部APIとの通信
   - Webhook処理

3. **エンドツーエンドフローの確認**
   - ユーザー認証からチャット処理まで
   - 完全なビジネスフロー

## 現在の実装状況

### 実装済み統合テスト

**現在未実装**

統合テストは現在実装されていません。

### 必要な統合テスト

## 1. データベース統合テスト

### テスト対象

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| データベース接続 | 接続・切断の確認 | 高 |
| リポジトリ実装 | CRUD操作の確認 | 高 |
| トランザクション | トランザクション処理 | 中 |
| マイグレーション | スキーマ変更の確認 | 中 |

### 必要なテストケース

```python
# データベース接続テスト
def test_database_connection():
    """データベース接続のテスト"""

def test_database_migration():
    """データベースマイグレーションのテスト"""

# リポジトリ統合テスト
def test_user_repository_integration():
    """ユーザーリポジトリの統合テスト"""

def test_chat_message_repository_integration():
    """チャットメッセージリポジトリの統合テスト"""

def test_reply_suggestion_repository_integration():
    """返信案リポジトリの統合テスト"""

def test_subscription_repository_integration():
    """サブスクリプションリポジトリの統合テスト"""
```

## 2. 外部API統合テスト

### Microsoft Graph API統合

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| 認証フロー | OAuth2認証の確認 | 高 |
| チャット取得 | チャットメッセージの取得 | 高 |
| メッセージ送信 | 返信メッセージの送信 | 高 |
| Webhook登録 | サブスクリプション登録 | 中 |

### Claude API統合

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| 返信生成 | AI返信の生成 | 高 |
| 品質評価 | 返信品質の評価 | 中 |
| エラーハンドリング | API エラーの処理 | 中 |

### MCPサーバー統合

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| サーバー接続 | MCPサーバーとの接続 | 高 |
| コマンド実行 | MCPコマンドの実行 | 高 |
| レスポンス処理 | MCPレスポンスの処理 | 中 |

### 必要なテストケース

```python
# Microsoft Graph API統合テスト
def test_microsoft_graph_auth_integration():
    """Microsoft Graph認証の統合テスト"""

def test_microsoft_graph_chat_integration():
    """Microsoft Graphチャット機能の統合テスト"""

def test_microsoft_graph_webhook_integration():
    """Microsoft Graph Webhookの統合テスト"""

# Claude API統合テスト
def test_claude_api_reply_generation():
    """Claude API返信生成の統合テスト"""

def test_claude_api_quality_evaluation():
    """Claude API品質評価の統合テスト"""

# MCPサーバー統合テスト
def test_mcp_server_connection():
    """MCPサーバー接続の統合テスト"""

def test_mcp_server_command_execution():
    """MCPサーバーコマンド実行の統合テスト"""
```

## 3. Webhook処理統合テスト

### テスト対象

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| Webhook受信 | メッセージ受信処理 | 高 |
| 署名検証 | セキュリティ検証 | 高 |
| メッセージ処理 | 受信メッセージの処理 | 高 |
| 返信生成 | AI返信の生成・送信 | 高 |

### 必要なテストケース

```python
# Webhook処理統合テスト
def test_webhook_message_reception():
    """Webhookメッセージ受信の統合テスト"""

def test_webhook_signature_verification():
    """Webhook署名検証の統合テスト"""

def test_webhook_message_processing():
    """Webhookメッセージ処理の統合テスト"""

def test_webhook_reply_generation():
    """Webhook返信生成の統合テスト"""
```

## 4. 認証フロー統合テスト

### Azure AD認証

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| ログインフロー | ユーザーログイン | 高 |
| トークン管理 | アクセストークンの管理 | 高 |
| セッション管理 | ユーザーセッションの管理 | 中 |
| 権限確認 | ユーザー権限の確認 | 中 |

### 必要なテストケース

```python
# 認証フロー統合テスト
def test_azure_ad_login_flow():
    """Azure ADログインフローの統合テスト"""

def test_azure_ad_token_management():
    """Azure ADトークン管理の統合テスト"""

def test_azure_ad_session_management():
    """Azure ADセッション管理の統合テスト"""

def test_azure_ad_permission_check():
    """Azure AD権限確認の統合テスト"""
```

## 5. スケジューラー統合テスト

### バッチ処理

| 対象 | テスト内容 | 優先度 |
|------|-----------|--------|
| 返信生成バッチ | 定期的な返信生成 | 中 |
| サブスクリプション更新 | 期限切れサブスクリプションの更新 | 中 |
| ログローテーション | ログファイルのローテーション | 低 |

### 必要なテストケース

```python
# スケジューラー統合テスト
def test_reply_generation_batch():
    """返信生成バッチの統合テスト"""

def test_subscription_renewal_batch():
    """サブスクリプション更新バッチの統合テスト"""

def test_log_rotation_batch():
    """ログローテーションバッチの統合テスト"""
```

## 統合テスト実装計画

### Phase 1: 高優先度 (2-4週間)

1. **データベース統合テスト**
   - データベース接続テスト
   - リポジトリ実装テスト
   - 目標: 基本的なCRUD操作の確認

2. **Microsoft Graph API統合テスト**
   - 認証フローテスト
   - チャット機能テスト
   - 目標: 基本的なAPI通信の確認

3. **Webhook処理統合テスト**
   - メッセージ受信テスト
   - 署名検証テスト
   - 目標: セキュアなWebhook処理の確認

### Phase 2: 中優先度 (4-6週間)

1. **Claude API統合テスト**
   - 返信生成テスト
   - 品質評価テスト
   - 目標: AI機能の動作確認

2. **MCPサーバー統合テスト**
   - サーバー接続テスト
   - コマンド実行テスト
   - 目標: MCP機能の動作確認

3. **認証フロー統合テスト**
   - セッション管理テスト
   - 権限確認テスト
   - 目標: セキュリティ機能の確認

### Phase 3: 低優先度 (6-8週間)

1. **スケジューラー統合テスト**
   - バッチ処理テスト
   - ログローテーションテスト
   - 目標: 運用機能の確認

2. **エンドツーエンド統合テスト**
   - 完全なユーザーフロー
   - エラー処理フロー
   - 目標: システム全体の動作確認

## 統合テスト環境

### テストデータベース

```python
# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///./test_auto_chat_maker.db"

# テスト用データベース初期化
def setup_test_database():
    """テスト用データベースの初期化"""
    pass

def teardown_test_database():
    """テスト用データベースのクリーンアップ"""
    pass
```

### モック外部API

```python
# 外部APIのモック設定
@pytest.fixture
def mock_microsoft_graph_api():
    """Microsoft Graph APIのモック"""
    pass

@pytest.fixture
def mock_claude_api():
    """Claude APIのモック"""
    pass

@pytest.fixture
def mock_mcp_server():
    """MCPサーバーのモック"""
    pass
```

### テスト用Webhook

```python
# テスト用Webhook設定
TEST_WEBHOOK_SECRET = "test-webhook-secret"
TEST_WEBHOOK_ENDPOINT = "/api/test/webhook"

def create_test_webhook_payload():
    """テスト用Webhookペイロードの作成"""
    pass
```

## 統合テスト実行方法

### 実行コマンド

```bash
# 全統合テスト実行
pytest tests/integration/ -v

# 特定カテゴリの統合テスト実行
pytest tests/integration/test_database.py -v
pytest tests/integration/test_external_api.py -v
pytest tests/integration/test_webhook.py -v

# カバレッジ付き統合テスト実行
pytest tests/integration/ --cov=src --cov-report=html
```

### テスト実行順序

1. **データベース統合テスト**
2. **外部API統合テスト**
3. **Webhook処理統合テスト**
4. **認証フロー統合テスト**
5. **スケジューラー統合テスト**

## 品質基準

### 統合テストの品質基準

1. **実行時間**: 10分以内
2. **成功率**: 100%
3. **カバレッジ**: 70%以上
4. **独立性**: 各テストは独立して実行可能

### 成功指標

- ✅ **データベース操作**: 正常にCRUD操作が実行される
- ✅ **外部API通信**: 正常にAPI通信が実行される
- ✅ **Webhook処理**: 正常にWebhookが処理される
- ✅ **認証フロー**: 正常に認証が実行される
- ✅ **エラーハンドリング**: 適切にエラーが処理される

## 関連ドキュメント

- [テストケース概要](./test-case-overview.md)
- [単体テストケース詳細](./unit-test-cases.md)
- [テストカバレッジ分析](./test-coverage-analysis.md)
- [テスト実装計画](./test-implementation-plan.md)
