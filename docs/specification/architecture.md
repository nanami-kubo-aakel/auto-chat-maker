# アーキテクチャ設計書

## 概要

AI Teamsチャットアシスタントシステムは、クリーンアーキテクチャ（Clean Architecture）に基づいて設計されています。システムは拡張性を重視し、将来的なOutlookメール対応も容易に追加できる設計となっています。

## アーキテクチャ理論

### クリーンアーキテクチャ（Clean Architecture）

Robert C. Martin（Uncle Bob）が提唱したアーキテクチャパターンを採用しています。

#### 特徴
- **依存関係の方向**: 内側（ドメイン）に向かって依存
- **レイヤー分離**: 関心事の分離による保守性向上
- **テスタビリティ**: 各レイヤーの独立したテストが可能
- **フレームワーク独立性**: ビジネスロジックがフレームワークに依存しない
- **拡張性**: プラグイン形式での新機能追加が可能

#### レイヤー構成
```
Entities (ドメイン) ← Use Cases (アプリケーション) ← Interface Adapters (インフラ) ← Frameworks & Drivers (フレームワーク)
```

## ディレクトリ構造

```
src/auto_chat_maker/
├── __init__.py
├── api/                        # フレームワーク & ドライバー層
│   ├── __init__.py
│   ├── controllers/            # HTTPリクエスト処理
│   │   └── __init__.py
│   ├── middleware/             # 認証、ログ、エラーハンドリング
│   │   └── __init__.py
│   └── routes.py               # APIルーティング定義
│
├── application/                # アプリケーション層
│   ├── __init__.py
│   ├── use_cases/              # ユースケース（ビジネスプロセス）
│   │   └── __init__.py
│   └── schedulers/             # 定期実行処理
│       └── __init__.py
│
├── domain/                     # エンティティ層（ドメイン層）
│   ├── __init__.py
│   ├── models/                 # ドメインモデル（エンティティ）
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
API → アプリケーション → ドメイン ← インフラストラクチャ
```

- 内側のレイヤーは外側のレイヤーに依存しない
- 外側のレイヤーは内側のレイヤーのインターフェースに依存
- 依存関係は内側に向かって流れる
- プラグインはドメイン層のインターフェースに依存

## 設計原則

### 1. 依存性逆転の原則（Dependency Inversion Principle）
- 高レベルのモジュールは低レベルのモジュールに依存しない
- 両方とも抽象に依存する
- 抽象は詳細に依存しない

### 2. 単一責任の原則（Single Responsibility Principle）
- 各クラスは1つの責任を持つ
- 各レイヤーは明確な責任を持つ
- 各プラグインは特定のメッセージタイプを処理する

### 3. 開放閉鎖の原則（Open-Closed Principle）
- 拡張に対して開いている（新しいプラグインの追加）
- 修正に対して閉じている（既存コードの変更不要）

### 4. リスコフ置換の原則（Liskov Substitution Principle）
- サブタイプは基底タイプと置換可能
- プラグインは共通インターフェースを満たす

### 5. インターフェース分離の原則（Interface Segregation Principle）
- クライアントは使用しないインターフェースに依存しない
- プラグインインターフェースは必要最小限のメソッドのみ定義

## 拡張性設計

### 段階的拡張計画

#### Phase 1: Teamsチャット対応（現在）
- Teamsチャットの自動検知・返信案生成
- 基本的なAI判定・生成機能
- ユーザーインターフェース

#### Phase 2: Outlookメール対応（将来）
- メール検知・返信機能の追加
- 共通AI判定・生成ロジックの活用
- 統合UIでの管理

#### Phase 3: その他Microsoft 365サービス対応
- ToDo、カレンダー等への対応
- 統合的なコミュニケーション管理

### 共通基盤設計

#### メッセージ処理の共通インターフェース
- プラグイン形式での実装
- 設定による機能の有効/無効切り替え

#### AI判定・生成ロジックの再利用
- メッセージタイプに依存しない共通ロジック
- プラグイン固有の前処理・後処理

#### 通知・UIシステムの統一
- 統合的な通知管理
- メッセージタイプ別の表示制御

#### データベース設計の拡張性
- メッセージタイプによる拡張
- 共通テーブルとプラグイン固有テーブルの分離

## 更新履歴

- 初版作成: 2024年12月
- Teams対応化: 2024年12月 - Teamsチャットベースに変更、プラグインアーキテクチャを追加
- 最終更新: 2024年12月
- 更新者: 開発チーム
