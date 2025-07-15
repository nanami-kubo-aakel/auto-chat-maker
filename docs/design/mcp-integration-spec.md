# MCPサーバー連携仕様書

## 概要

Auto Chat MakerシステムとMicrosoft MCPサーバー（ms-365-mcp-server）との連携仕様を定義します。MCPサーバーを経由してMicrosoft Graph APIにアクセスし、Teamsチャットのメッセージ取得・送信を行います。

## MCPサーバー概要

### 役割
- Microsoft Graph APIとクライアントの中継プロキシサーバー
- Graph API呼び出しを統一的に扱うラッパーサーバー
- 認証・認可の簡素化

### 通信プロトコル
- **プロトコル**: HTTP/HTTPS
- **認証**: OAuth2（Azure AD）
- **データ形式**: JSON

## 設定管理

### 環境変数設定
```env
# MCP Server Settings
MCP_SERVER_URL=http://localhost:3000
MCP_CLIENT_ID=your_client_id
MCP_CLIENT_SECRET=your_client_secret
MCP_TENANT_ID=your_tenant_id

# Azure AD Settings
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback

# Webhook Settings
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_SUBSCRIPTION_DURATION=3600
```

### 設定クラス
```python
class MCPSettings(BaseSettings):
    mcp_server_url: str
    mcp_client_id: str
    mcp_client_secret: str
    mcp_tenant_id: str

    class Config:
        env_file = ".env"
```

## APIエンドポイント仕様

### 1. チャットメッセージ取得

#### エンドポイント
```
GET /mcp/chat/{chat_id}/message/{message_id}
```

#### リクエストヘッダー
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### レスポンス
```json
{
  "message_id": "msg_001",
  "content": "メッセージ内容",
  "sender": "送信者名",
  "sent_at": "2024-12-01T10:00:00Z",
  "thread_id": "thread_001",
  "channel_id": "channel_001",
  "team_id": "team_001",
  "message_type": "text"
}
```

### 2. チャット返信送信

#### エンドポイント
```
POST /mcp/chat/{chat_id}/reply
```

#### リクエストヘッダー
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### リクエストボディ
```json
{
  "message": "返信内容",
  "reply_to_message_id": "msg_001"
}
```

#### レスポンス
```json
{
  "success": true,
  "message_id": "msg_002",
  "sent_at": "2024-12-01T10:05:00Z"
}
```

### 3. チャット一覧取得

#### エンドポイント
```
GET /mcp/chat/{chat_id}/messages
```

#### クエリパラメータ
- `limit`: 取得件数（デフォルト: 50）
- `before`: 指定時刻以前のメッセージ
- `after`: 指定時刻以降のメッセージ

#### レスポンス
```json
{
  "messages": [
    {
      "message_id": "msg_001",
      "content": "メッセージ内容",
      "sender": "送信者名",
      "sent_at": "2024-12-01T10:00:00Z"
    }
  ],
  "has_more": false
}
```

## 認証フロー

### OAuth2認証フロー
1. **認証URL生成**: Azure AD認証URLの生成
2. **ユーザー認証**: ブラウザでの認証実行
3. **コールバック処理**: 認証コードの受信
4. **トークン取得**: アクセストークン・リフレッシュトークンの取得
5. **トークン保存**: メモリキャッシュまたは環境変数での保存

### トークン管理
```python
class TokenManager:
    def get_access_token(self) -> str:
        """アクセストークンを取得"""
        pass

    def refresh_token(self) -> bool:
        """リフレッシュトークンでトークン更新"""
        pass

    def is_token_valid(self) -> bool:
        """トークンの有効性チェック"""
        pass
```

## エラーハンドリング

### エラーコード
| エラーコード | 説明 | 対応 |
|-------------|------|------|
| 401 | 認証エラー | トークン再取得 |
| 403 | 権限エラー | 権限確認 |
| 404 | リソース未発見 | リソース存在確認 |
| 429 | レート制限 | リトライ処理 |
| 500 | サーバーエラー | リトライ処理 |

### リトライ戦略
```python
class RetryStrategy:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0

    def should_retry(self, error: Exception) -> bool:
        """リトライすべきエラーか判定"""
        pass

    def get_delay(self, attempt: int) -> float:
        """リトライ間隔を計算"""
        pass
```

## ログ出力

### ログレベル
- **DEBUG**: 詳細な通信ログ
- **INFO**: 正常な処理ログ
- **WARNING**: 警告ログ
- **ERROR**: エラーログ

### ログ項目
```python
logger.info("MCP API呼び出し", extra={
    "endpoint": "/mcp/chat/123/message/456",
    "method": "GET",
    "response_time": 0.5,
    "status_code": 200
})
```

## パフォーマンス要件

### 応答時間
- **メッセージ取得**: 3秒以内
- **返信送信**: 5秒以内
- **一覧取得**: 5秒以内

### スループット
- **同時リクエスト数**: 10リクエスト/分
- **1日あたりの処理件数**: 1000件程度

## セキュリティ要件

### 通信暗号化
- **プロトコル**: HTTPS必須
- **証明書**: 有効なSSL証明書

### 認証・認可
- **認証方式**: OAuth2
- **トークン管理**: セキュアなトークン保存
- **権限管理**: 最小権限の原則

### データ保護
- **機密情報**: 環境変数での管理
- **ログ出力**: 機密情報の除外
- **エラーメッセージ**: 詳細情報の制限

## テスト仕様

### 単体テスト
- MCPクライアントクラスのテスト
- 認証フローのテスト
- エラーハンドリングのテスト

### 統合テスト
- MCPサーバーとの通信テスト
- エンドツーエンドテスト
- パフォーマンステスト

### モックサーバー
```python
class MockMCPServer:
    def __init__(self):
        self.messages = {}
        self.replies = []

    def get_message(self, chat_id: str, message_id: str) -> dict:
        """メッセージ取得のモック"""
        pass

    def send_reply(self, chat_id: str, message: str) -> dict:
        """返信送信のモック"""
        pass
```

## 更新履歴

- 初版作成: 2024年12月
- MCPサーバー連携仕様: 2024年12月 - 基本仕様の定義
- 最終更新: 2024年12月
- 更新者: 開発チーム
