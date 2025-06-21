# 技術仕様書

## 概要

AIメールアシスタントシステムの技術的な実装仕様を定義します。

## 技術スタック

### バックエンド
- **言語**: Python 3.8以上
- **Webフレームワーク**: FastAPI
- **ORM**: SQLAlchemy
- **データバリデーション**: Pydantic
- **非同期処理**: Celery + Redis
- **ログ**: structlog

### 外部サービス連携
- **Microsoft Graph API**: メール・スレッド・サブスクリプション管理
- **MCPサーバー**: `ms-365-mcp-server` - Outlook連携
- **AIサービス**: Claude API（Anthropic）

### 開発・運用ツール
- **コード品質**: Black, isort, flake8, mypy
- **テスト**: pytest
- **プレコミットフック**: pre-commit
- **ドキュメント**: Sphinx

## アーキテクチャ詳細

### レイヤー構成

#### 1. API層（Frameworks & Drivers）
- **FastAPI**: Webフレームワーク
- **Pydantic**: リクエスト/レスポンスモデル
- **認証**: OAuth2 + JWT
- **バリデーション**: Pydanticバリデーター

#### 2. アプリケーション層（Use Cases）
- **ユースケース**: ビジネスプロセスの調整
- **Celery**: 非同期タスク処理
- **Redis**: タスクキュー・キャッシュ

#### 3. ドメイン層（Entities）
- **ドメインモデル**: Pydanticベースのエンティティ
- **値オブジェクト**: 不変オブジェクト
- **リポジトリインターフェース**: 抽象基底クラス

#### 4. インフラストラクチャ層（Interface Adapters）
- **HTTPクライアント**: aiohttp/httpx
- **データベース**: PostgreSQL + SQLAlchemy
- **外部API**: 専用クライアントクラス

## データベース設計

### 主要テーブル

#### users
- id: UUID (Primary Key)
- email: VARCHAR(255) (Unique)
- name: VARCHAR(255)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

#### emails
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- message_id: VARCHAR(255) (Unique)
- subject: TEXT
- body: TEXT
- sender: VARCHAR(255)
- received_at: TIMESTAMP
- processed_at: TIMESTAMP
- created_at: TIMESTAMP

#### reply_suggestions
- id: UUID (Primary Key)
- email_id: UUID (Foreign Key)
- content: TEXT
- confidence_score: DECIMAL(3,2)
- selected: BOOLEAN
- created_at: TIMESTAMP

#### subscriptions
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- subscription_id: VARCHAR(255)
- resource: VARCHAR(255)
- expires_at: TIMESTAMP
- created_at: TIMESTAMP

## API仕様

### エンドポイント

#### POST /api/webhook/microsoft-graph
Microsoft Graph Webhook受信エンドポイント

**リクエスト**:
```json
{
  "value": [
    {
      "subscriptionId": "string",
      "subscriptionExpirationDateTime": "string",
      "changeType": "created",
      "resource": "string",
      "clientState": "string"
    }
  ]
}
```

**レスポンス**: 200 OK

#### GET /api/emails
ユーザーのメール一覧取得

**レスポンス**:
```json
{
  "emails": [
    {
      "id": "uuid",
      "subject": "string",
      "sender": "string",
      "received_at": "timestamp",
      "reply_suggestions": [
        {
          "id": "uuid",
          "content": "string",
          "confidence_score": 0.95
        }
      ]
    }
  ]
}
```

#### POST /api/emails/{email_id}/reply
メール返信送信

**リクエスト**:
```json
{
  "content": "string",
  "suggestion_id": "uuid"
}
```

## 外部サービス連携

### Microsoft Graph API

#### 認証
- OAuth2認証フロー
- アクセストークンの管理
- リフレッシュトークンの自動更新

#### Webhook設定
- サブスクリプション作成・更新
- 60分間隔での自動更新
- HMAC検証によるセキュリティ

### MCPサーバー連携

#### メール取得
```python
# メール情報取得
GET /mcp/ms-365/mail/{message_id}
```

#### メール返信
```python
# メール返信送信
POST /mcp/ms-365/mail/reply
{
  "messageId": "string",
  "content": "string"
}
```

### Claude API連携

#### 返信要否判断
```python
# プロンプト例
"""
以下のメールに対して返信が必要かどうかを判断してください。
返信が必要な場合は「REPLY_NEEDED」、不要な場合は「NO_REPLY」を返してください。

メール内容:
{email_content}
"""
```

#### 返信案生成
```python
# プロンプト例
"""
以下のメールに対して、3件の返信案を生成してください。
各返信案は自然で丁寧な日本語で、100文字以内で作成してください。

メール内容:
{email_content}

返信案1:
返信案2:
返信案3:
"""
```

## セキュリティ仕様

### 認証・認可
- OAuth2認証（Microsoft Graph）
- JWTトークン管理
- ロールベースアクセス制御

### データ保護
- 個人情報の暗号化
- 通信のHTTPS化
- ログの機密情報マスキング

### Webhookセキュリティ
- HMAC署名検証
- リクエスト元IP制限
- レート制限

## パフォーマンス仕様

### レスポンス時間
- API応答時間: 500ms以内
- AI処理時間: 5秒以内
- メール処理時間: 10秒以内

### スループット
- 同時接続数: 100
- 1日あたりのメール処理数: 10,000件

### 可用性
- 稼働率: 99.9%
- 障害復旧時間: 30分以内

## 監視・ログ

### ログ出力
- アプリケーションログ: structlog
- アクセスログ: FastAPI標準
- エラーログ: 構造化ログ

### メトリクス
- API応答時間
- エラー率
- 処理件数
- 外部API呼び出し回数

## 更新履歴

- 初版作成: 2024年12月
- 最終更新: 2024年12月
- 更新者: 開発チーム
