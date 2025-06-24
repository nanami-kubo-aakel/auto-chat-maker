# Phase 2: コア機能実装 - 詳細クラス設計書

## 概要

Auto Chat MakerシステムのPhase 2（コア機能実装）における詳細なクラス設計を定義します。AI機能とWebhook処理の実装に焦点を当て、各クラスと関数の役割をクリーンアーキテクチャの原則に従って設計します。

## 設計方針

### AI機能設計原則
- **判定と生成の分離**: 返信要否判定と返信案生成を独立した機能として設計
- **プロンプト管理**: プロンプトの設計・管理を一元化
- **品質管理**: 生成結果の品質評価とフィルタリング
- **非同期処理**: 長時間のAI処理を非同期で実行

### Webhook処理設計原則
- **リアルタイム処理**: Webhook受信時の即座な処理
- **エラーハンドリング**: 処理失敗時の適切な対応
- **重複防止**: 同一メッセージの重複処理防止
- **プラグイン対応**: メッセージタイプ別の処理分岐

## 1. AI機能実装 (infrastructure/external/ & application/services/)

### 1.1 Claude APIクライアント

#### `infrastructure/external/claude_client.py`

**クラス**: `ClaudeClient`
**責任**: Claude APIとの通信管理

**主要メソッド**:
- `generate_response(prompt: str, max_tokens: int) -> str`
  - プロンプトに基づいてAI応答を生成
- `analyze_message(content: str) -> Dict[str, Any]`
  - メッセージ内容を分析して構造化データを返却
- `validate_response(response: str) -> bool`
  - 生成された応答の妥当性を検証

**依存関係**:
- `aiohttp` - HTTP通信
- `AppLogger` - ログ出力
- `ClaudeSettings` - Claude API設定

### 1.2 AI判定・生成サービス

#### `application/services/ai_service.py`

**クラス**: `AIService`
**責任**: AI機能の統合管理

**主要メソッド**:
- `should_reply(message_content: str, context: Dict[str, Any]) -> bool`
  - 返信が必要かどうかを判定
- `generate_reply_suggestions(message_content: str, context: Dict[str, Any]) -> List[ReplySuggestion]`
  - 複数の返信案を生成
- `evaluate_suggestion_quality(suggestion: ReplySuggestion) -> float`
  - 返信案の品質を評価
- `filter_suggestions(suggestions: List[ReplySuggestion], min_confidence: float) -> List[ReplySuggestion]`
  - 信頼度の低い返信案をフィルタリング

**依存関係**:
- `ClaudeClient` - Claude APIクライアント
- `ReplySuggestionRepository` - 返信案リポジトリ
- `AppLogger` - ログ出力

### 1.3 プロンプト管理

#### `application/services/prompt_service.py`

**クラス**: `PromptService`
**責任**: AIプロンプトの設計・管理

**主要メソッド**:
- `get_reply_judgment_prompt(message_content: str, context: Dict[str, Any]) -> str`
  - 返信要否判定用プロンプトを生成
- `get_reply_generation_prompt(message_content: str, context: Dict[str, Any]) -> str`
  - 返信案生成用プロンプトを生成
- `get_quality_evaluation_prompt(suggestion: ReplySuggestion) -> str`
  - 品質評価用プロンプトを生成
- `update_prompt_template(template_name: str, new_template: str) -> None`
  - プロンプトテンプレートを更新

**依存関係**:
- `PromptTemplateRepository` - プロンプトテンプレートリポジトリ
- `AppLogger` - ログ出力

## 2. メッセージ処理ユースケース (application/use_cases/)

### 2.1 メッセージ処理ユースケース

#### `application/use_cases/message_processor.py`

**クラス**: `MessageProcessor`
**責任**: チャットメッセージの処理フロー管理

**主要メソッド**:
- `process_message(message_data: Dict[str, Any]) -> ProcessedMessage`
  - メッセージの処理フローを実行
- `extract_message_context(message_data: Dict[str, Any]) -> Dict[str, Any]`
  - メッセージからコンテキスト情報を抽出
- `validate_message(message_data: Dict[str, Any]) -> bool`
  - メッセージデータの妥当性を検証
- `mark_message_processed(message_id: str) -> None`
  - メッセージを処理済みとしてマーク

**依存関係**:
- `AIService` - AIサービス
- `ChatMessageRepository` - チャットメッセージリポジトリ
- `ReplySuggestionRepository` - 返信案リポジトリ
- `AppLogger` - ログ出力

### 2.2 返信案生成ユースケース

#### `application/use_cases/reply_generator.py`

**クラス**: `ReplyGenerator`
**責任**: AIによる返信案生成の管理

**主要メソッド**:
- `generate_replies_for_message(message_id: str) -> List[ReplySuggestion]`
  - 指定メッセージに対する返信案を生成
- `generate_multiple_suggestions(content: str, count: int) -> List[ReplySuggestion]`
  - 複数の返信案を生成
- `refine_suggestion(suggestion_id: str, feedback: str) -> ReplySuggestion`
  - フィードバックに基づいて返信案を改善
- `merge_suggestions(suggestion_ids: List[str]) -> ReplySuggestion`
  - 複数の返信案を統合

**依存関係**:
- `AIService` - AIサービス
- `PromptService` - プロンプトサービス
- `ReplySuggestionRepository` - 返信案リポジトリ
- `AppLogger` - ログ出力

### 2.3 返信送信ユースケース

#### `application/use_cases/reply_sender.py`

**クラス**: `ReplySender`
**責任**: 選択された返信の送信管理

**主要メソッド**:
- `send_reply(message_id: str, reply_content: str) -> bool`
  - 返信を送信
- `send_selected_suggestion(suggestion_id: str) -> bool`
  - 選択された返信案を送信
- `validate_reply_content(content: str) -> bool`
  - 送信前の返信内容を検証
- `track_reply_sent(message_id: str, reply_content: str) -> None`
  - 送信履歴を記録

**依存関係**:
- `MCPClient` - MCPクライアント
- `ReplySuggestionRepository` - 返信案リポジトリ
- `ChatMessageRepository` - チャットメッセージリポジトリ
- `AppLogger` - ログ出力

## 3. Webhook処理実装 (api/routes/ & application/use_cases/)

### 3.1 Webhook受信エンドポイント

#### `api/routes/webhook.py`

**クラス**: `WebhookController`
**責任**: Webhook受信の処理

**主要メソッド**:
- `handle_microsoft_graph_webhook(request: Request) -> JSONResponse`
  - Microsoft Graph Webhookの受信処理
- `verify_webhook_signature(request: Request) -> bool`
  - Webhook署名の検証
- `extract_webhook_data(request: Request) -> Dict[str, Any]`
  - Webhookデータの抽出
- `process_webhook_notification(notification_data: Dict[str, Any]) -> None`
  - Webhook通知の処理

**依存関係**:
- `WebhookProcessor` - Webhook処理ユースケース
- `AppLogger` - ログ出力

### 3.2 Webhook処理ユースケース

#### `application/use_cases/webhook_processor.py`

**クラス**: `WebhookProcessor`
**責任**: Webhook通知の処理フロー管理

**主要メソッド**:
- `process_notification(notification_data: Dict[str, Any]) -> None`
  - Webhook通知の処理フローを実行
- `handle_chat_message_created(message_data: Dict[str, Any]) -> None`
  - チャットメッセージ作成通知の処理
- `handle_chat_message_updated(message_data: Dict[str, Any]) -> None`
  - チャットメッセージ更新通知の処理
- `handle_chat_message_deleted(message_data: Dict[str, Any]) -> None`
  - チャットメッセージ削除通知の処理
- `is_duplicate_notification(notification_id: str) -> bool`
  - 重複通知かどうかを判定

**依存関係**:
- `MessageProcessor` - メッセージ処理ユースケース
- `ChatMessageRepository` - チャットメッセージリポジトリ
- `AppLogger` - ログ出力

## 4. Teamsプラグイン実装 (infrastructure/plugins/)

### 4.1 Teamsチャットプラグイン

#### `infrastructure/plugins/teams_plugin.py`

**クラス**: `TeamsChatPlugin`
**責任**: Teamsチャット固有の処理

**主要メソッド**:
- `process_message(message_data: Dict[str, Any]) -> Dict[str, Any]`
  - Teamsメッセージの処理
- `extract_teams_context(message_data: Dict[str, Any]) -> Dict[str, Any]`
  - Teams固有のコンテキスト情報を抽出
- `format_reply_for_teams(content: str) -> str`
  - Teams用に返信内容をフォーマット
- `handle_teams_attachments(message_data: Dict[str, Any]) -> List[str]`
  - Teams添付ファイルの処理
- `get_teams_user_info(user_id: str) -> Dict[str, Any]`
  - Teamsユーザー情報の取得

**依存関係**:
- `MCPClient` - MCPクライアント
- `GraphClient` - Graph APIクライアント
- `AppLogger` - ログ出力

### 4.2 プラグイン管理

#### `infrastructure/plugins/plugin_manager.py`

**クラス**: `PluginManager`
**責任**: プラグインの登録・管理

**主要メソッド**:
- `register_plugin(plugin: MessageProcessor) -> None`
  - プラグインを登録
- `get_plugin(message_type: str) -> Optional[MessageProcessor]`
  - メッセージタイプに対応するプラグインを取得
- `list_available_plugins() -> List[str]`
  - 利用可能なプラグイン一覧を取得
- `enable_plugin(plugin_name: str) -> bool`
  - プラグインを有効化
- `disable_plugin(plugin_name: str) -> bool`
  - プラグインを無効化

**依存関係**:
- `MessageProcessor` - メッセージ処理インターフェース
- `AppLogger` - ログ出力

## 5. Graph APIクライアント (infrastructure/external/)

### 5.1 Graph APIクライアント

#### `infrastructure/external/graph_client.py`

**クラス**: `GraphClient`
**責任**: Microsoft Graph APIとの通信管理

**主要メソッド**:
- `create_subscription(resource: str, change_type: str, webhook_url: str) -> Dict[str, Any]`
  - Webhookサブスクリプションを作成
- `renew_subscription(subscription_id: str) -> Dict[str, Any]`
  - サブスクリプションを更新
- `delete_subscription(subscription_id: str) -> bool`
  - サブスクリプションを削除
- `get_team_info(team_id: str) -> Dict[str, Any]`
  - チーム情報を取得
- `get_channel_info(team_id: str, channel_id: str) -> Dict[str, Any]`
  - チャンネル情報を取得
- `get_user_profile(user_id: str) -> Dict[str, Any]`
  - ユーザープロフィールを取得

**依存関係**:
- `aiohttp` - HTTP通信
- `TokenManager` - トークン管理
- `AppLogger` - ログ出力

## 6. 実装順序と依存関係

### 実装順序
1. **infrastructure/external/claude_client.py** - Claude APIクライアント（依存なし）
2. **application/services/prompt_service.py** - プロンプト管理（Claudeクライアントに依存）
3. **application/services/ai_service.py** - AIサービス（Claudeクライアント、プロンプトサービスに依存）
4. **infrastructure/external/graph_client.py** - Graph APIクライアント（トークン管理に依存）
5. **infrastructure/plugins/teams_plugin.py** - Teamsプラグイン（MCPクライアント、Graphクライアントに依存）
6. **infrastructure/plugins/plugin_manager.py** - プラグイン管理（Teamsプラグインに依存）
7. **application/use_cases/message_processor.py** - メッセージ処理（AIサービス、プラグイン管理に依存）
8. **application/use_cases/reply_generator.py** - 返信案生成（AIサービスに依存）
9. **application/use_cases/reply_sender.py** - 返信送信（MCPクライアントに依存）
10. **application/use_cases/webhook_processor.py** - Webhook処理（メッセージ処理に依存）
11. **api/routes/webhook.py** - Webhook受信（Webhook処理に依存）

### 依存関係図
```
infrastructure/external/claude_client.py
    ↓
application/services/prompt_service.py
    ↓
application/services/ai_service.py
    ↓
infrastructure/external/graph_client.py
    ↓
infrastructure/plugins/teams_plugin.py
    ↓
infrastructure/plugins/plugin_manager.py
    ↓
application/use_cases/message_processor.py
    ↓
application/use_cases/reply_generator.py
application/use_cases/reply_sender.py
    ↓
application/use_cases/webhook_processor.py
    ↓
api/routes/webhook.py
```

## 7. データフロー設計

### 7.1 Webhook受信フロー
```
Microsoft Graph → WebhookController → WebhookProcessor → MessageProcessor → AIService → ReplyGenerator
```

### 7.2 返信案生成フロー
```
MessageProcessor → AIService → PromptService → ClaudeClient → ReplySuggestionRepository
```

### 7.3 返信送信フロー
```
ReplySender → MCPClient → Teams → ReplySuggestionRepository (更新)
```

## 8. エラーハンドリング戦略

### 8.1 AI処理エラー
- **Claude API制限**: レート制限時の待機処理
- **プロンプトエラー**: プロンプトテンプレートの検証
- **生成失敗**: フォールバックプロンプトの使用

### 8.2 Webhook処理エラー
- **重複通知**: 重複チェックによる処理スキップ
- **データ不整合**: バリデーションエラー時のログ出力
- **処理失敗**: リトライ機能による再処理

### 8.3 外部APIエラー
- **MCP接続エラー**: リトライ機能による再接続
- **Graph API制限**: レート制限時の待機処理
- **認証エラー**: トークン更新による再認証

## 9. テスト戦略

### 9.1 単体テスト対象
- **AIサービス**: 判定・生成ロジックのテスト
- **Webhook処理**: 通知処理フローのテスト
- **プラグイン**: Teams固有処理のテスト
- **APIクライアント**: 外部API通信のテスト

### 9.2 統合テスト対象
- **エンドツーエンドフロー**: Webhook受信から返信送信まで
- **AI連携**: Claude APIとの実際の通信テスト
- **プラグイン統合**: プラグイン管理とメッセージ処理の統合

### 9.3 テスト方針
- **モック活用**: 外部APIのモック化
- **非同期テスト**: 非同期処理のテスト
- **エラーケース**: 異常系のテスト
- **パフォーマンステスト**: 処理時間の測定

## 更新履歴

- 初版作成: 2024年12月
- 更新者: 開発チーム
