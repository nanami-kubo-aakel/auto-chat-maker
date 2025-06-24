# Phase 3: データ管理・UI - 詳細クラス設計書

## 概要

Auto Chat MakerシステムのPhase 3（データ管理・UI）における詳細なクラス設計を定義します。SQLiteデータベース実装とWeb UIの設計に焦点を当て、各クラスと関数の役割をクリーンアーキテクチャの原則に従って設計します。

## 設計方針

### データベース設計原則
- **ORM活用**: SQLAlchemyによる型安全なデータアクセス
- **マイグレーション**: Alembicによるスキーマ管理
- **接続管理**: 接続プールとトランザクション管理
- **パフォーマンス**: インデックスとクエリ最適化

### Web UI設計原則
- **シンプルな構成**: FastAPI + HTML/JavaScriptによる軽量UI
- **レスポンシブ**: モバイル対応のレスポンシブデザイン
- **ユーザビリティ**: 直感的な操作とフィードバック
- **非同期更新**: AJAXによる動的なコンテンツ更新

## 1. データベース実装 (infrastructure/database/)

### 1.1 SQLAlchemyモデル

#### `infrastructure/database/models.py`

**クラス**: `Base`
**責任**: SQLAlchemy基本モデルクラス

**主要メソッド**:
- `__repr__() -> str` - モデルの文字列表現
- `to_dict() -> Dict[str, Any]` - 辞書形式でのデータ取得
- `from_dict(data: Dict[str, Any]) -> None` - 辞書からデータ設定

**クラス**: `UserModel`
**責任**: ユーザーテーブルのSQLAlchemyモデル

**主要メソッド**:
- `__init__(email: str, name: str)` - ユーザーモデルの初期化
- `update_name(name: str) -> None` - ユーザー名の更新
- `is_active() -> bool` - ユーザーの有効性チェック

**クラス**: `ChatMessageModel`
**責任**: チャットメッセージテーブルのSQLAlchemyモデル

**主要メソッド**:
- `__init__(user_id: str, message_id: str, content: str, sender: str, thread_id: str)` - メッセージモデルの初期化
- `mark_as_processed() -> None` - 処理済みとしてマーク
- `get_reply_suggestions() -> List[ReplySuggestionModel]` - 関連する返信案を取得
- `is_reply_needed() -> bool` - 返信が必要かどうか判定

**クラス**: `ReplySuggestionModel`
**責任**: 返信案テーブルのSQLAlchemyモデル

**主要メソッド**:
- `__init__(chat_message_id: str, content: str, confidence_score: float)` - 返信案モデルの初期化
- `select() -> None` - 返信案を選択
- `deselect() -> None` - 返信案の選択を解除
- `is_high_confidence() -> bool` - 高信頼度かどうか判定

**クラス**: `SubscriptionModel`
**責任**: サブスクリプションテーブルのSQLAlchemyモデル

**主要メソッド**:
- `__init__(user_id: str, subscription_id: str, resource: str, resource_type: str, expires_at: datetime)` - サブスクリプションモデルの初期化
- `is_expired() -> bool` - 期限切れかどうか判定
- `days_until_expiry() -> int` - 期限までの日数を取得
- `renew(expires_at: datetime) -> None` - サブスクリプションを更新

**依存関係**:
- `sqlalchemy` - ORMライブラリ
- `datetime` - 時間管理

### 1.2 データベース設定

#### `infrastructure/database/connection.py`

**クラス**: `DatabaseManager`
**責任**: データベース接続の管理

**主要メソッド**:
- `__init__(database_url: str)` - データベースマネージャーの初期化
- `get_engine() -> Engine` - SQLAlchemyエンジンを取得
- `get_session() -> Session` - データベースセッションを取得
- `create_tables() -> None` - テーブルを作成
- `drop_tables() -> None` - テーブルを削除
- `close() -> None` - 接続を閉じる

**クラス**: `DatabaseSession`
**責任**: データベースセッションの管理

**主要メソッド**:
- `__enter__() -> Session` - コンテキストマネージャー開始
- `__exit__(exc_type, exc_val, exc_tb) -> None` - コンテキストマネージャー終了
- `commit() -> None` - トランザクションをコミット
- `rollback() -> None` - トランザクションをロールバック

**依存関係**:
- `sqlalchemy` - ORMライブラリ
- `sqlalchemy.orm` - セッション管理

### 1.3 リポジトリ実装

#### `infrastructure/database/repositories.py`

**クラス**: `SQLAlchemyUserRepository`
**責任**: ユーザーリポジトリのSQLAlchemy実装

**主要メソッド**:
- `save(user: User) -> User` - ユーザーを保存
- `find_by_id(user_id: str) -> Optional[User]` - IDでユーザーを検索
- `find_by_email(email: str) -> Optional[User]` - メールアドレスでユーザーを検索
- `find_all() -> List[User]` - 全ユーザーを取得
- `delete(user_id: str) -> bool` - ユーザーを削除
- `update(user: User) -> User` - ユーザーを更新

**クラス**: `SQLAlchemyChatMessageRepository`
**責任**: チャットメッセージリポジトリのSQLAlchemy実装

**主要メソッド**:
- `save(message: ChatMessage) -> ChatMessage` - メッセージを保存
- `find_by_id(message_id: str) -> Optional[ChatMessage]` - IDでメッセージを検索
- `find_by_user_id(user_id: str, limit: int = 100) -> List[ChatMessage]` - ユーザーIDでメッセージを検索
- `find_unprocessed() -> List[ChatMessage]` - 未処理メッセージを検索
- `find_by_thread_id(thread_id: str) -> List[ChatMessage]` - スレッドIDでメッセージを検索
- `delete(message_id: str) -> bool` - メッセージを削除
- `mark_as_processed(message_id: str) -> None` - メッセージを処理済みとしてマーク

**クラス**: `SQLAlchemyReplySuggestionRepository`
**責任**: 返信案リポジトリのSQLAlchemy実装

**主要メソッド**:
- `save(suggestion: ReplySuggestion) -> ReplySuggestion` - 返信案を保存
- `find_by_chat_message_id(chat_message_id: str) -> List[ReplySuggestion]` - チャットメッセージIDで返信案を検索
- `find_selected(chat_message_id: str) -> Optional[ReplySuggestion]` - 選択済み返信案を検索
- `select_suggestion(suggestion_id: str) -> None` - 返信案を選択
- `deselect_suggestions(chat_message_id: str) -> None` - 返信案の選択を解除
- `delete(suggestion_id: str) -> bool` - 返信案を削除
- `find_high_confidence(chat_message_id: str, min_confidence: float = 0.8) -> List[ReplySuggestion]` - 高信頼度返信案を検索

**クラス**: `SQLAlchemySubscriptionRepository`
**責任**: サブスクリプションリポジトリのSQLAlchemy実装

**主要メソッド**:
- `save(subscription: Subscription) -> Subscription` - サブスクリプションを保存
- `find_by_id(subscription_id: str) -> Optional[Subscription]` - IDでサブスクリプションを検索
- `find_by_user_id(user_id: str) -> List[Subscription]` - ユーザーIDでサブスクリプションを検索
- `find_expired() -> List[Subscription]` - 期限切れサブスクリプションを検索
- `find_active() -> List[Subscription]` - 有効なサブスクリプションを検索
- `delete(subscription_id: str) -> bool` - サブスクリプションを削除
- `update_expiry(subscription_id: str, expires_at: datetime) -> None` - 有効期限を更新

**依存関係**:
- `UserRepository` - ユーザーリポジトリインターフェース
- `ChatMessageRepository` - チャットメッセージリポジトリインターフェース
- `ReplySuggestionRepository` - 返信案リポジトリインターフェース
- `SubscriptionRepository` - サブスクリプションリポジトリインターフェース
- `DatabaseManager` - データベース管理

### 1.4 マイグレーション管理

#### `infrastructure/database/migrations/env.py`

**クラス**: `MigrationManager`
**責任**: データベースマイグレーションの管理

**主要メソッド**:
- `create_migration(message: str) -> str` - 新しいマイグレーションを作成
- `upgrade(target: str = "head") -> None` - マイグレーションを適用
- `downgrade(target: str) -> None` - マイグレーションを戻す
- `current() -> str` - 現在のマイグレーション版を取得
- `history() -> List[str]` - マイグレーション履歴を取得

**依存関係**:
- `alembic` - マイグレーションライブラリ
- `DatabaseManager` - データベース管理

## 2. Web UI実装 (templates/ & api/routes/)

### 2.1 ベーステンプレート

#### `templates/base.html`

**クラス**: `BaseTemplate`
**責任**: 全ページの基本レイアウト

**主要ブロック**:
- `{% block title %}` - ページタイトル
- `{% block head %}` - ヘッドセクション（CSS、メタタグ）
- `{% block content %}` - メインコンテンツ
- `{% block scripts %}` - スクリプトセクション（JavaScript）

**主要機能**:
- レスポンシブデザイン対応
- ナビゲーションメニュー
- フラッシュメッセージ表示
- ユーザー認証状態表示

### 2.2 チャット一覧ページ

#### `templates/chat_list.html`

**クラス**: `ChatListTemplate`
**責任**: チャットメッセージ一覧の表示

**主要ブロック**:
- `{% block chat_messages %}` - チャットメッセージ一覧
- `{% block filters %}` - フィルター機能
- `{% block pagination %}` - ページネーション

**主要機能**:
- メッセージの一覧表示
- 送信者、日時、内容でのフィルタリング
- 処理状態での絞り込み
- ページネーション機能
- リアルタイム更新（WebSocket）

**JavaScript機能**:
- `loadChatMessages(page: number, filters: object)` - チャットメッセージの非同期読み込み
- `applyFilters(filters: object)` - フィルターの適用
- `refreshMessages()` - メッセージ一覧の更新
- `markAsProcessed(messageId: string)` - メッセージを処理済みとしてマーク

### 2.3 返信案表示ページ

#### `templates/reply_suggestions.html`

**クラス**: `ReplySuggestionsTemplate`
**責任**: 返信案の表示・選択・編集

**主要ブロック**:
- `{% block message_details %}` - 元メッセージの詳細
- `{% block suggestions %}` - 返信案一覧
- `{% block actions %}` - アクションボタン

**主要機能**:
- 元メッセージの詳細表示
- 複数返信案の表示
- 返信案の選択・編集機能
- 信頼度スコアの表示
- 返信送信機能

**JavaScript機能**:
- `loadSuggestions(messageId: string)` - 返信案の非同期読み込み
- `selectSuggestion(suggestionId: string)` - 返信案の選択
- `editSuggestion(suggestionId: string, content: string)` - 返信案の編集
- `sendReply(suggestionId: string)` - 返信の送信
- `generateNewSuggestions(messageId: string)` - 新しい返信案の生成

### 2.4 UIエンドポイント

#### `api/routes/ui.py`

**クラス**: `UIController`
**責任**: Web UIのエンドポイント管理

**主要メソッド**:
- `render_chat_list(request: Request, page: int = 1, filters: Dict[str, Any] = None) -> HTMLResponse`
  - チャット一覧ページをレンダリング
- `render_reply_suggestions(request: Request, message_id: str) -> HTMLResponse`
  - 返信案表示ページをレンダリング
- `render_dashboard(request: Request) -> HTMLResponse`
  - ダッシュボードページをレンダリング
- `render_settings(request: Request) -> HTMLResponse`
  - 設定ページをレンダリング

**クラス**: `ChatListController`
**責任**: チャット一覧のAPI管理

**主要メソッド**:
- `get_chat_messages(page: int = 1, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]`
  - チャットメッセージ一覧を取得
- `get_message_count(filters: Dict[str, Any] = None) -> int`
  - メッセージ数を取得
- `mark_message_processed(message_id: str) -> bool`
  - メッセージを処理済みとしてマーク
- `delete_message(message_id: str) -> bool`
  - メッセージを削除

**クラス**: `ReplySuggestionsController`
**責任**: 返信案のAPI管理

**主要メソッド**:
- `get_suggestions(message_id: str) -> List[Dict[str, Any]]`
  - 返信案一覧を取得
- `select_suggestion(suggestion_id: str) -> bool`
  - 返信案を選択
- `edit_suggestion(suggestion_id: str, content: str) -> bool`
  - 返信案を編集
- `send_reply(suggestion_id: str) -> bool`
  - 返信を送信
- `generate_suggestions(message_id: str) -> List[Dict[str, Any]]`
  - 新しい返信案を生成

**依存関係**:
- `ChatMessageRepository` - チャットメッセージリポジトリ
- `ReplySuggestionRepository` - 返信案リポジトリ
- `ReplyGenerator` - 返信案生成ユースケース
- `ReplySender` - 返信送信ユースケース
- `Jinja2Templates` - テンプレートエンジン

### 2.5 チャット管理API

#### `api/routes/chat.py`

**クラス**: `ChatAPIController`
**責任**: チャット管理のRESTful API

**主要メソッド**:
- `get_messages(skip: int = 0, limit: int = 100, user_id: Optional[str] = None) -> List[Dict[str, Any]]`
  - メッセージ一覧を取得（RESTful API）
- `get_message(message_id: str) -> Dict[str, Any]`
  - 特定メッセージを取得
- `update_message(message_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]`
  - メッセージを更新
- `delete_message(message_id: str) -> bool`
  - メッセージを削除
- `get_message_suggestions(message_id: str) -> List[Dict[str, Any]]`
  - メッセージの返信案を取得

**クラス**: `ReplyAPIController`
**責任**: 返信管理のRESTful API

**主要メソッド**:
- `get_suggestions(message_id: str) -> List[Dict[str, Any]]`
  - 返信案一覧を取得
- `create_suggestion(message_id: str, suggestion_data: Dict[str, Any]) -> Dict[str, Any]`
  - 新しい返信案を作成
- `update_suggestion(suggestion_id: str, suggestion_data: Dict[str, Any]) -> Dict[str, Any]`
  - 返信案を更新
- `delete_suggestion(suggestion_id: str) -> bool`
  - 返信案を削除
- `select_suggestion(suggestion_id: str) -> bool`
  - 返信案を選択
- `send_reply(suggestion_id: str) -> bool`
  - 返信を送信

**依存関係**:
- `ChatMessageRepository` - チャットメッセージリポジトリ
- `ReplySuggestionRepository` - 返信案リポジトリ
- `ReplyGenerator` - 返信案生成ユースケース
- `ReplySender` - 返信送信ユースケース

## 3. 静的ファイル管理 (static/)

### 3.1 CSS管理

#### `static/css/main.css`

**クラス**: `MainStylesheet`
**責任**: メインスタイルシート

**主要セクション**:
- `.header` - ヘッダー部分のスタイル
- `.chat-list` - チャット一覧のスタイル
- `.message-item` - メッセージ項目のスタイル
- `.suggestion-item` - 返信案項目のスタイル
- `.button` - ボタンのスタイル
- `.form` - フォームのスタイル

**主要機能**:
- レスポンシブデザイン
- ダークモード対応
- アニメーション効果
- アクセシビリティ対応

### 3.2 JavaScript管理

#### `static/js/chat.js`

**クラス**: `ChatManager`
**責任**: チャット機能のJavaScript管理

**主要メソッド**:
- `loadMessages(page: number, filters: object)` - メッセージの非同期読み込み
- `applyFilters(filters: object)` - フィルターの適用
- `refreshMessages()` - メッセージ一覧の更新
- `markAsProcessed(messageId: string)` - メッセージを処理済みとしてマーク
- `deleteMessage(messageId: string)` - メッセージの削除

#### `static/js/suggestions.js`

**クラス**: `SuggestionsManager`
**責任**: 返信案機能のJavaScript管理

**主要メソッド**:
- `loadSuggestions(messageId: string)` - 返信案の非同期読み込み
- `selectSuggestion(suggestionId: string)` - 返信案の選択
- `editSuggestion(suggestionId: string, content: string)` - 返信案の編集
- `sendReply(suggestionId: string)` - 返信の送信
- `generateNewSuggestions(messageId: string)` - 新しい返信案の生成

#### `static/js/api.js`

**クラス**: `APIClient`
**責任**: API通信のJavaScript管理

**主要メソッド**:
- `get(url: string, params: object)` - GETリクエスト
- `post(url: string, data: object)` - POSTリクエスト
- `put(url: string, data: object)` - PUTリクエスト
- `delete(url: string)` - DELETEリクエスト
- `handleResponse(response: Response)` - レスポンス処理
- `handleError(error: Error)` - エラー処理

## 4. 実装順序と依存関係

### 実装順序
1. **infrastructure/database/models.py** - SQLAlchemyモデル（依存なし）
2. **infrastructure/database/connection.py** - データベース接続管理（モデルに依存）
3. **infrastructure/database/repositories.py** - リポジトリ実装（接続管理に依存）
4. **infrastructure/database/migrations/env.py** - マイグレーション管理（接続管理に依存）
5. **templates/base.html** - ベーステンプレート（依存なし）
6. **static/css/main.css** - メインスタイルシート（依存なし）
7. **static/js/api.js** - API通信クライアント（依存なし）
8. **templates/chat_list.html** - チャット一覧テンプレート（ベーステンプレートに依存）
9. **templates/reply_suggestions.html** - 返信案テンプレート（ベーステンプレートに依存）
10. **static/js/chat.js** - チャット機能JavaScript（APIクライアントに依存）
11. **static/js/suggestions.js** - 返信案機能JavaScript（APIクライアントに依存）
12. **api/routes/ui.py** - UIエンドポイント（リポジトリ、テンプレートに依存）
13. **api/routes/chat.py** - チャット管理API（リポジトリ、ユースケースに依存）

### 依存関係図
```
infrastructure/database/models.py
    ↓
infrastructure/database/connection.py
    ↓
infrastructure/database/repositories.py
infrastructure/database/migrations/env.py
    ↓
templates/base.html
static/css/main.css
static/js/api.js
    ↓
templates/chat_list.html
templates/reply_suggestions.html
    ↓
static/js/chat.js
static/js/suggestions.js
    ↓
api/routes/ui.py
api/routes/chat.py
```

## 5. データフロー設計

### 5.1 チャット一覧表示フロー
```
UI Controller → Chat Message Repository → Database → SQLAlchemy Models → Template Rendering
```

### 5.2 返信案表示フロー
```
UI Controller → Reply Suggestion Repository → Database → Template Rendering → JavaScript
```

### 5.3 返信送信フロー
```
JavaScript → API Controller → Reply Sender → MCP Client → Teams
```

## 6. エラーハンドリング戦略

### 6.1 データベースエラー
- **接続エラー**: 接続プールによる再接続
- **トランザクションエラー**: 自動ロールバック
- **制約違反**: バリデーションエラーの適切な表示

### 6.2 UIエラー
- **API通信エラー**: ユーザーフレンドリーなエラーメッセージ
- **バリデーションエラー**: フォームエラーの表示
- **JavaScriptエラー**: グレースフルデグラデーション

### 6.3 パフォーマンス対策
- **ページネーション**: 大量データの分割表示
- **キャッシュ**: 頻繁にアクセスされるデータのキャッシュ
- **非同期処理**: 重い処理の非同期実行

## 7. テスト戦略

### 7.1 データベーステスト
- **モデルテスト**: SQLAlchemyモデルの動作テスト
- **リポジトリテスト**: データアクセスロジックのテスト
- **マイグレーションテスト**: スキーマ変更のテスト

### 7.2 UIテスト
- **テンプレートテスト**: レンダリング結果のテスト
- **JavaScriptテスト**: クライアントサイド機能のテスト
- **統合テスト**: エンドツーエンドのUIテスト

### 7.3 APIテスト
- **エンドポイントテスト**: RESTful APIの動作テスト
- **認証テスト**: 認証・認可のテスト
- **バリデーションテスト**: 入力データの検証テスト

## 更新履歴

- 初版作成: 2024年12月
- 更新者: 開発チーム
