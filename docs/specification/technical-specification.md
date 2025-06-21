# 技術仕様書

## 概要

AI Teamsチャットアシスタントシステムの技術的な実装仕様を定義します。システムは拡張性を重視し、将来的なOutlookメール対応も容易に追加できるアーキテクチャを採用しています。

## 技術スタック

### バックエンド
- **言語**: Python 3.8以上
- **Webフレームワーク**: FastAPI
- **ORM**: SQLAlchemy
- **データバリデーション**: Pydantic
- **非同期処理**: Celery + Redis
- **ログ**: structlog

### 外部サービス連携
- **Microsoft Graph API**: Teamsチャット・スレッド・サブスクリプション管理
- **MCPサーバー**: `ms-365-mcp-server` - Teams連携
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

#### chat_messages
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- message_id: VARCHAR(255) (Unique)
- content: TEXT
- sender: VARCHAR(255)
- thread_id: VARCHAR(255)
- message_type: VARCHAR(50) (text, image, file, etc.)
- sent_at: TIMESTAMP
- processed_at: TIMESTAMP
- created_at: TIMESTAMP

#### reply_suggestions
- id: UUID (Primary Key)
- chat_message_id: UUID (Foreign Key)
- content: TEXT
- confidence_score: DECIMAL(3,2)
- selected: BOOLEAN
- created_at: TIMESTAMP

#### subscriptions
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- subscription_id: VARCHAR(255)
- resource: VARCHAR(255)
- resource_type: VARCHAR(50) (chat, mail, etc.)
- expires_at: TIMESTAMP
- created_at: TIMESTAMP

#### message_types
- id: UUID (Primary Key)
- type_name: VARCHAR(50) (chat, mail, etc.)
- description: TEXT
- is_active: BOOLEAN
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

#### GET /api/chat-messages
ユーザーのチャットメッセージ一覧取得

**レスポンス**:
```json
{
  "chat_messages": [
    {
      "id": "uuid",
      "content": "string",
      "sender": "string",
      "sent_at": "timestamp",
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

#### POST /api/chat-messages/{message_id}/reply
チャットメッセージ返信送信

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

#### チャットメッセージ取得
```python
# チャットメッセージ情報取得
GET /mcp/ms-365/chat/{message_id}
```

#### チャット返信
```python
# チャット返信送信
POST /mcp/ms-365/chat/reply
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
以下のチャットメッセージに対して返信が必要かどうかを判断してください。
返信が必要な場合は「REPLY_NEEDED」、不要な場合は「NO_REPLY」を返してください。

チャットメッセージ内容:
{message_content}
"""
```

#### 返信案生成
```python
# プロンプト例
"""
以下のチャットメッセージに対して、3件の返信案を生成してください。
チャットの文脈とトーンを考慮した自然な返信案を作成してください。

チャットメッセージ内容:
{message_content}
"""
```

## 拡張性設計

### プラグインアーキテクチャ

#### メッセージ処理プラグイン
```python
from abc import ABC, abstractmethod

class MessageProcessor(ABC):
    @abstractmethod
    def process_message(self, message: dict) -> dict:
        pass

    @abstractmethod
    def send_reply(self, message_id: str, content: str) -> bool:
        pass
```

#### Teamsチャット処理プラグイン
```python
class TeamsChatProcessor(MessageProcessor):
    def process_message(self, message: dict) -> dict:
        # Teamsチャット固有の処理
        pass

    def send_reply(self, message_id: str, content: str) -> bool:
        # Teamsチャット返信処理
        pass
```

#### 将来的なメール処理プラグイン
```python
class OutlookMailProcessor(MessageProcessor):
    def process_message(self, message: dict) -> dict:
        # Outlookメール固有の処理
        pass

    def send_reply(self, message_id: str, content: str) -> bool:
        # Outlookメール返信処理
        pass
```

### 設定管理

#### 機能有効化設定
```python
class FeatureConfig:
    teams_chat_enabled: bool = True
    outlook_mail_enabled: bool = False  # 将来的に有効化
    ai_service_enabled: bool = True
```

## パフォーマンス要件

### 処理時間
- チャットメッセージ処理時間: 10秒以内
- AI判定・生成時間: 30秒以内
- 返信送信時間: 5秒以内

### スループット
- 1日あたりのチャットメッセージ処理数: 10,000件
- 同時処理可能ユーザー数: 100人以上

## セキュリティ要件

### 認証・認可
- Microsoft 365認証必須
- JWTトークンによるセッション管理
- ロールベースアクセス制御

### データ保護
- TLS 1.3以上での通信暗号化
- データベース保存時暗号化
- 機密情報のマスキング

## 更新履歴

- 初版作成: 2024年12月
- Teams対応化: 2024年12月 - Teamsチャットベースに変更、拡張性設計を追加
- 最終更新: 2024年12月
- 更新者: 開発チーム
