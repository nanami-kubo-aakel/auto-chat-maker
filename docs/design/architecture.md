# アーキテクチャ設計書

## 概要

AI Teamsチャットアシスタントシステムは、クリーンアーキテクチャ（Clean Architecture）に基づいて設計されています。システムは拡張性を重視し、将来的なOutlookメール対応も容易に追加できる設計となっています。

## アーキテクチャ理論

### クリーンアーキテクチャ（Clean Architecture）

Robert C. Martin（Uncle Bob）が提唱したアーキテクチャパターンを採用しています。

#### 設計原則
- **依存関係の方向**: 内側のレイヤーは外側のレイヤーに依存しない
- **フレームワーク独立性**: ビジネスロジックがフレームワークに依存しない
- **テスタビリティ**: 各レイヤーが独立してテスト可能
- **独立性**: データベースやUIの変更がビジネスロジックに影響しない

#### レイヤー構造
```
Entities (ドメイン) ← Use Cases (アプリケーション) ← Interface Adapters (インフラ) ← Frameworks & Drivers (フレームワーク)
```

## プロジェクト構造

```
src/auto_chat_maker/
├── api/                        # フレームワーク & ドライバー層
│   ├── __init__.py
│   ├── controllers/            # コントローラー
│   │   └── __init__.py
│   ├── middleware/             # ミドルウェア
│   │   └── __init__.py
│   └── routes.py               # ルーティング
│
├── application/                # アプリケーション層
│   ├── __init__.py
│   ├── use_cases/              # ユースケース
│   │   └── __init__.py
│   └── schedulers/             # 定期実行処理
│       └── __init__.py
│
├── domain/                     # ドメイン層
│   ├── __init__.py
│   ├── models/                 # エンティティ
│   │   └── __init__.py
│   ├── repositories/           # リポジトリインターフェース
│   │   └── __init__.py
│   ├── value_objects/          # 値オブジェクト
│   │   └── __init__.py
│   └── plugins/                # プラグインインターフェース
│       └── __init__.py
│
├── infrastructure/             # インターフェースアダプター層
│   ├── __init__.py
│   ├── repositories/           # リポジトリ実装
│   │   └── __init__.py
│   ├── external/               # 外部サービス連携
│   │   └── __init__.py
│   ├── database/               # データベース関連
│   │   └── __init__.py
│   └── plugins/                # プラグイン実装
│       ├── teams_chat/         # Teamsチャット処理プラグイン
│       └── outlook_mail/       # Outlookメール処理プラグイン（将来）
│
├── services/                   # ドメインサービス層
│   └── __init__.py
│
├── utils/                      # ユーティリティ層
│   └── __init__.py
│
├── config/                     # 設定層
│   └── __init__.py
│
└── main.py                     # アプリケーションエントリーポイント
```

## 技術スタックの選択理由

### FastAPIの採用理由

#### 1. 軽量で高速
- **ローカル試行に最適**: 軽量なフレームワークでローカル環境での動作が高速
- **起動時間**: 数秒での起動が可能
- **メモリ使用量**: 最小限のメモリ消費

#### 2. 非同期対応
- **組み込み非同期機能**: Celery + Redisのような重い非同期処理システムが不要
- **同時リクエスト処理**: 複数のリクエストを効率的に処理
- **Webhook処理**: 非同期でのWebhook受信処理に適している

#### 3. 自動ドキュメント生成
- **OpenAPI/Swagger**: 自動的にAPI仕様書を生成
- **開発効率**: API開発・テストが効率的
- **チーム開発**: 仕様書の共有が容易

#### 4. 型安全性
- **Pydantic**: 強力な型チェックとバリデーション
- **開発時エラー検出**: 実行時エラーを開発時に発見
- **IDEサポート**: 優れたIDEサポート

#### 5. 統合環境
- **バックエンド・フロントエンド統合**: 同一プロジェクトで管理
- **テンプレート機能**: HTMLテンプレートによるUI実装
- **開発効率**: フルスタック開発が効率的

## MCPサーバー連携設計

### MCPサーバー連携アーキテクチャ

#### 1. 連携概要
```
Auto Chat Maker ←→ MCPサーバー ←→ Microsoft Graph API ←→ Teams
```

#### 2. 連携コンポーネント

##### MCPクライアント実装
```python
class MCPClient:
    """MCPサーバーとの通信を管理するクライアント"""

    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def get_chat_message(self, message_id: str) -> Dict[str, Any]:
        """チャットメッセージを取得"""
        url = f"{self.server_url}/mcp/ms-365/chat/{message_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def send_chat_reply(self, message_id: str, content: str) -> bool:
        """チャット返信を送信"""
        url = f"{self.server_url}/mcp/ms-365/chat/reply"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"message_id": message_id, "content": content}

        async with self.session.post(url, headers=headers, json=data) as response:
            return response.status == 200
```

##### Teamsチャットプラグイン統合
```python
class TeamsChatProcessor(MessageProcessor):
    """Teamsチャット処理プラグイン（MCP連携版）"""

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Teamsチャットメッセージを処理"""
        # MCP経由でメッセージ詳細を取得
        message_id = message.get("message_id")
        chat_message = await self.mcp_client.get_chat_message(message_id)

        return {
            "message_id": message_id,
            "content": chat_message.get("content"),
            "sender": chat_message.get("sender"),
            "thread_id": chat_message.get("thread_id"),
            "sent_at": chat_message.get("sent_at")
        }

    async def send_reply(self, message_id: str, content: str) -> bool:
        """Teamsチャット返信を送信"""
        return await self.mcp_client.send_chat_reply(message_id, content)
```

#### 3. エラーハンドリング

##### 接続エラー処理
```python
class MCPConnectionError(Exception):
    """MCPサーバー接続エラー"""
    pass

class MCPClient:
    async def get_chat_message(self, message_id: str) -> Dict[str, Any]:
        try:
            # MCPサーバーとの通信
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise MCPConnectionError(f"MCP server error: {response.status}")
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection failed: {e}")
```

##### リトライ機能
```python
class MCPClient:
    async def send_chat_reply_with_retry(self, message_id: str, content: str, max_retries: int = 3) -> bool:
        """リトライ機能付きチャット返信送信"""
        for attempt in range(max_retries):
            try:
                return await self.send_chat_reply(message_id, content)
            except MCPConnectionError as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # 指数バックオフ
```

#### 4. 設定管理

##### 環境変数設定
```python
class Settings:
    mcp_server_url: Optional[str] = None
    mcp_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
```

##### 設定検証
```python
def validate_mcp_settings(settings: Settings) -> bool:
    """MCP設定の検証"""
    if not settings.mcp_server_url:
        raise ValueError("MCP server URL is required")
    if not settings.mcp_api_key:
        raise ValueError("MCP API key is required")
    return True
```

## レイヤー詳細

### 1. API層（Frameworks & Drivers）

**責任**: HTTPリクエストの受信とレスポンスの送信

**含まれるもの**:
- HTTPエンドポイント
- リクエスト/レスポンスの変換
- 認証・認可
- バリデーション

**依存関係**: アプリケーション層に依存

### 2. アプリケーション層（Use Cases）

**責任**: ビジネスプロセスの調整

**含まれるもの**:
- ユースケース（ビジネスプロセス）
- 定期実行処理
- ワークフロー制御
- プラグイン管理

**依存関係**: ドメイン層に依存

### 3. ドメイン層（Entities）

**責任**: ビジネスルールとエンティティ

**含まれるもの**:
- ドメインモデル（エンティティ）
- 値オブジェクト
- ドメインサービス
- リポジトリインターフェース
- プラグインインターフェース

**依存関係**: 他のレイヤーに依存しない

### 4. インフラストラクチャ層（Interface Adapters）

**責任**: 外部システムとの連携

**含まれるもの**:
- リポジトリ実装
- 外部APIクライアント
- データベース接続
- ファイルシステム操作
- プラグイン実装

**依存関係**: ドメイン層に依存

### 5. サービス層（Domain Services）

**責任**: ドメインロジックの実装

**含まれるもの**:
- 複雑なビジネスロジック
- 複数のエンティティを跨ぐ処理
- AI判定・生成ロジック

**依存関係**: ドメイン層に依存

### 6. ユーティリティ層

**責任**: 共通機能の提供

**含まれるもの**:
- ログ出力
- セキュリティ機能
- ヘルパー関数

**依存関係**: 他のレイヤーに依存しない

### 7. 設定層

**責任**: アプリケーション設定の管理

**含まれるもの**:
- 環境変数
- 設定ファイル
- 定数定義
- プラグイン設定

**依存関係**: 他のレイヤーに依存しない

## プラグインアーキテクチャ

### プラグイン設計原則

#### 1. 共通インターフェース
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class MessageProcessor(ABC):
    """メッセージ処理プラグインの共通インターフェース"""

    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """メッセージを処理する"""
        pass

    @abstractmethod
    def send_reply(self, message_id: str, content: str) -> bool:
        """返信を送信する"""
        pass

    @abstractmethod
    def get_message_type(self) -> str:
        """メッセージタイプを取得する"""
        pass
```

#### 2. Teamsチャットプラグイン
```python
class TeamsChatProcessor(MessageProcessor):
    """Teamsチャット処理プラグイン"""

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Teamsチャット固有の処理
        return processed_message

    def send_reply(self, message_id: str, content: str) -> bool:
        # Teamsチャット返信処理
        return success

    def get_message_type(self) -> str:
        return "teams_chat"
```

#### 3. 将来的なメールプラグイン
```python
class OutlookMailProcessor(MessageProcessor):
    """Outlookメール処理プラグイン（将来対応）"""

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Outlookメール固有の処理
        return processed_message

    def send_reply(self, message_id: str, content: str) -> bool:
        # Outlookメール返信処理
        return success

    def get_message_type(self) -> str:
        return "outlook_mail"
```

### プラグイン管理

#### プラグイン登録
```python
class PluginManager:
    """プラグイン管理クラス"""

    def __init__(self):
        self._plugins: Dict[str, MessageProcessor] = {}

    def register_plugin(self, plugin: MessageProcessor):
        """プラグインを登録する"""
        self._plugins[plugin.get_message_type()] = plugin

    def get_plugin(self, message_type: str) -> Optional[MessageProcessor]:
        """プラグインを取得する"""
        return self._plugins.get(message_type)
```

## 依存関係の方向

```
┌─────────────────────────────────────────────────────────────┐
│                    Frameworks & Drivers                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FastAPI   │  │   MCP       │  │   Claude    │        │
│  │   Web UI    │  │   Server    │  │   API       │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Interface Adapters                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Controllers │  │ Repositories│  │   External  │        │
│  │ Middleware  │  │   Database  │  │   Services  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Use Cases                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Process     │  │ Generate    │  │ Send Reply  │        │
│  │ Message     │  │ Reply       │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Entities                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Message   │  │   Reply     │  │   User      │        │
│  │   Thread    │  │   Option    │  │   Settings  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## データフロー

### 1. メッセージ受信フロー
```
Webhook → API層(受信) → アプリケーション層(処理) → ドメイン層(エンティティ作成) → インフラ層(DB保存) → データ層(SQLite)
```

### 2. 返信生成フロー
```
AI判定 → アプリケーション層(生成) → ドメイン層(返信案エンティティ) → インフラ層(DB保存) → データ層(SQLite)
```

### 3. 返信送信フロー
```
UI選択 → アプリケーション層(送信) → インフラ層(MCP連携) → 外部連携層(MCPサーバー) → Teams(メッセージ送信)
```

## セキュリティ設計

### 認証・認可
- **OAuth2認証**: Microsoft 365認証を使用
- **API認証**: MCPサーバーとの認証
- **セッション管理**: サーバーサイドセッション

### データ保護
- **暗号化**: 機密データの暗号化
- **アクセス制御**: ロールベースアクセス制御
- **監査ログ**: 操作履歴の記録

## パフォーマンス設計

### 非同期処理
- **FastAPI非同期**: 同時リクエスト処理
- **バックグラウンド処理**: 重い処理の非同期実行
- **キャッシュ**: メモリキャッシュによる高速化

### スケーラビリティ
- **水平スケーリング**: 複数インスタンス対応
- **データベース**: 読み取り専用レプリカ対応
- **負荷分散**: ロードバランサー対応

## 監視・ログ

### ログ設計
- **構造化ログ**: structlogによる構造化ログ
- **ログレベル**: 適切なログレベルの設定
- **ログローテーション**: ログファイルの自動ローテーション

### メトリクス
- **パフォーマンス**: レスポンス時間の監視
- **エラー率**: エラー発生率の監視
- **リソース使用量**: CPU・メモリ使用量の監視

## 更新履歴

- 初版作成: 2024年12月
- Teams対応化: 2024年12月 - Teamsチャットベースに変更、プラグインアーキテクチャを追加
- FastAPI採用理由追加: 2024年12月 - 技術スタック選択理由を詳細化
- MCP連携設計追加: 2024年12月 - MCPサーバー連携の詳細設計を追加
- 最終更新: 2024年12月
- 更新者: 開発チーム
