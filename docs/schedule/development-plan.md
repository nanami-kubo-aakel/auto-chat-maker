# 開発計画書

## 概要

Auto Chat Makerシステムの開発計画を定義します。ローカルでの試行を前提とし、クリーンアーキテクチャに基づく段階的実装により、効率的な開発を進めます。

## 開発理論

### 採用理論
- **クリーンアーキテクチャ**: 依存関係の方向を内側（ドメイン）に向け、レイヤーを明確に分離
- **段階的開発（Incremental Development）**: 機能を段階的に実装し、各段階で動作確認
- **テスト駆動開発（TDD）の要素**: AAAパターンによるテスト設計
- **ドメイン駆動設計（DDD）の要素**: エンティティ、値オブジェクト、リポジトリパターン

### 基本方針
- **段階的実装**: 機能を段階的に実装し、各段階で動作確認
- **軽量構成**: 最小限の技術スタックで高速開発
- **品質重視**: 各段階で十分なテストを実施
- **ドキュメント整備**: 実装と並行してドキュメントを整備

## ディレクトリ構造と実装計画

### プロジェクト構造
```
src/auto_chat_maker/
├── config/                    # 設定管理層
│   ├── __init__.py
│   ├── settings.py           # 基本設定クラス
│   ├── mcp_settings.py       # MCP設定クラス
│   └── azure_settings.py     # Azure AD設定クラス
├── utils/                     # ユーティリティ層
│   ├── __init__.py
│   ├── logger.py             # ログ設定
│   └── exceptions.py         # カスタム例外
├── domain/                    # ドメイン層
│   ├── models/               # エンティティ
│   │   ├── __init__.py
│   │   ├── user.py           # ユーザーエンティティ
│   │   ├── chat_message.py   # チャットメッセージエンティティ
│   │   ├── reply_suggestion.py # 返信案エンティティ
│   │   └── subscription.py   # サブスクリプションエンティティ
│   └── repositories/         # リポジトリインターフェース
│       ├── __init__.py
│       └── interfaces.py     # リポジトリインターフェース
├── application/               # アプリケーション層
│   ├── use_cases/            # ユースケース
│   │   ├── __init__.py
│   │   ├── message_processor.py # メッセージ処理ユースケース
│   │   ├── reply_generator.py   # 返信案生成ユースケース
│   │   ├── reply_sender.py      # 返信送信ユースケース
│   │   ├── webhook_manager.py   # Webhook管理ユースケース
│   │   └── webhook_processor.py # Webhook処理ユースケース
│   └── services/             # アプリケーションサービス
│       ├── __init__.py
│       ├── ai_service.py     # AI判定・生成サービス
│       └── subscription_service.py # サブスクリプション管理
├── infrastructure/            # インフラストラクチャ層
│   ├── external/             # 外部APIクライアント
│   │   ├── __init__.py
│   │   ├── mcp_client.py     # MCPクライアント
│   │   ├── claude_client.py  # Claude APIクライアント
│   │   ├── graph_client.py   # Graph APIクライアント
│   │   └── retry_handler.py  # リトライ機能
│   ├── auth/                 # 認証・認可
│   │   ├── __init__.py
│   │   ├── azure_ad.py       # Azure AD認証
│   │   ├── token_manager.py  # トークン管理
│   │   └── middleware.py     # 認証ミドルウェア
│   ├── database/             # データベース
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemyモデル
│   │   ├── repositories.py   # リポジトリ実装
│   │   └── migrations/       # Alembicマイグレーション
│   └── plugins/              # プラグイン
│       ├── __init__.py
│       └── teams_plugin.py   # Teamsプラグイン
├── api/                       # API層
│   ├── routes/               # ルーティング
│   │   ├── __init__.py
│   │   ├── health.py         # ヘルスチェック
│   │   ├── auth.py           # 認証エンドポイント
│   │   ├── webhook.py        # Webhook受信
│   │   ├── ui.py             # UIエンドポイント
│   │   └── chat.py           # チャット管理API
│   └── middleware/           # ミドルウェア
│       ├── __init__.py
│       └── error_handler.py  # エラーハンドリング
├── templates/                 # HTMLテンプレート
│   ├── base.html
│   ├── chat_list.html
│   └── reply_suggestions.html
├── main.py                   # FastAPIアプリケーション
└── __init__.py
```

## 実装フェーズ詳細

> **詳細設計書へのリンク**: 各フェーズの詳細なクラス設計については、以下の設計書を参照してください。
> - [Phase 1 クラス設計](../design/phase1-class-design.md) - 基盤構築の詳細クラス設計
> - [Phase 1.5 MCPサーバー設計](../design/phase1-5-mcp-server-design.md) - MCPサーバー開発の詳細設計
> - [Phase 1.6 MCP統合設計](../design/phase1-6-mcp-integration-design.md) - MCP連携の詳細実装
> - [Phase 2 コア機能設計](../design/phase2-core-functionality-design.md) - AI機能とWebhook処理の詳細設計
> - [Phase 3 データ・UI設計](../design/phase3-data-ui-design.md) - データベースとWeb UIの詳細設計

### Phase 1: 基盤構築（1-2週間）

> **詳細設計書**: [Phase 1 クラス設計](../design/phase1-class-design.md)

#### Week 1: プロジェクト基盤
**目標**: 基本的なアプリケーション構造の構築

**実装内容**:
```
Day 1-2: プロジェクト構造の整理
- src/auto_chat_maker/以下のディレクトリ構造作成
- 各ディレクトリの__init__.pyファイル作成
- 基本的な設定管理クラスの実装

実装ファイル:
- config/settings.py: 基本設定クラス
- utils/logger.py: ログ設定
- utils/exceptions.py: カスタム例外
- main.py: FastAPIアプリケーション基本構造

Day 3-4: FastAPIアプリケーションの基本実装
- main.pyの実装（FastAPIアプリケーション）
- 基本的なルーティング設定
- エラーハンドリングの実装

実装ファイル:
- api/middleware/error_handler.py: グローバルエラーハンドラー
- api/routes/health.py: ヘルスチェックエンドポイント
- main.py: ルーティング設定

Day 5: 基盤機能のテスト
- 各基盤機能の動作確認
- エラーケースのテスト
- ドキュメントの更新
```

#### Week 2: 外部連携基盤
**目標**: Azure AD認証基盤の実装

**実装内容**:
```
Day 1-2: Azure AD認証基盤の実装
- Azure AD認証基盤の実装
- 基本的な認証フローの実装
- 設定管理の詳細実装

実装ファイル:
- config/azure_settings.py: Azure AD設定クラス
- infrastructure/auth/azure_ad.py: Azure AD認証基盤
- infrastructure/auth/token_manager.py: トークン管理

Day 3-4: Webhook処理基盤の実装
- Microsoft Graph Webhook受信エンドポイント
- Webhook検証ロジックの実装
- 設定管理の詳細実装
- 環境変数の設定

実装ファイル:
- infrastructure/external/graph_client.py: Graph APIクライアント基盤
- api/routes/webhook.py: Webhook受信基盤
- api/routes/auth.py: 認証エンドポイント

Day 5: 基盤機能の統合テスト
- 全基盤機能の動作確認
- エラーケースのテスト
- データベーススキーマ実装
- ドキュメントの更新

実装ファイル:
- domain/models/user.py: ユーザーエンティティ
- domain/models/chat_message.py: チャットメッセージエンティティ
- domain/repositories/interfaces.py: リポジトリインターフェース
```

### Phase 1.5: MCPサーバー開発（2-3週間）

> **詳細設計書**: [Phase 1.5 MCPサーバー設計](../design/phase1-5-mcp-server-design.md)

**目標**: Microsoft Teams用MCPサーバーの開発

#### Week 3: MCPサーバー基盤開発
**実装内容**:
```
Day 1-2: MCPプロトコル実装
- MCPプロトコル仕様の理解と実装
- HTTP/HTTPS通信基盤の実装
- 基本的なエンドポイントの実装

実装ファイル:
- mcp-server/src/protocol/mcp_protocol.py: MCPプロトコル実装
- mcp-server/src/server/mcp_server.py: MCPサーバー基盤
- mcp-server/src/api/endpoints.py: 基本エンドポイント

Day 3-4: Microsoft Graph API連携
- Graph APIクライアントの実装
- Teamsチャット操作機能の実装
- 認証・認可機能の実装

実装ファイル:
- mcp-server/src/clients/graph_client.py: Graph APIクライアント
- mcp-server/src/services/teams_service.py: Teams操作サービス
- mcp-server/src/auth/oauth2_handler.py: OAuth2認証ハンドラー

Day 5: 基本機能のテスト
- MCPサーバーの起動・動作確認
- Graph API連携のテスト
- 認証機能のテスト
```

#### Week 4: MCPサーバー機能拡張
**実装内容**:
```
Day 1-2: Teamsチャット操作機能
- メッセージ取得機能の実装
- メッセージ送信機能の実装
- スレッド管理機能の実装

実装ファイル:
- mcp-server/src/services/chat_service.py: チャット操作サービス
- mcp-server/src/models/chat_message.py: チャットメッセージモデル
- mcp-server/src/api/chat_endpoints.py: チャットエンドポイント

Day 3-4: Webhook管理機能
- サブスクリプション作成・更新機能
- Webhook受信処理の実装
- 定期更新処理の実装

実装ファイル:
- mcp-server/src/services/webhook_service.py: Webhook管理サービス
- mcp-server/src/models/subscription.py: サブスクリプションモデル
- mcp-server/src/api/webhook_endpoints.py: Webhookエンドポイント

Day 5: セキュリティ・エラーハンドリング
- HTTPS通信の実装
- レート制限の実装
- エラーハンドリングの強化
- ログ・監査機能の実装

実装ファイル:
- mcp-server/src/security/rate_limiter.py: レート制限
- mcp-server/src/security/ssl_handler.py: SSL処理
- mcp-server/src/utils/logger.py: ログ機能
```

#### Week 5: MCPサーバー統合・テスト
**実装内容**:
```
Day 1-2: 統合テスト
- 全機能の統合テスト
- エラーケースのテスト
- パフォーマンステスト

Day 3-4: ドキュメント・デプロイ
- API仕様書の作成
- デプロイ手順の整備
- 設定ファイルの整備

Day 5: Auto Chat Makerとの連携テスト
- MCPクライアントとの通信テスト
- エンドツーエンドテスト
- 問題点の修正
```

### Phase 1.6: MCP連携詳細実装（1週間）

> **詳細設計書**: [Phase 1.6 MCP統合設計](../design/phase1-6-mcp-integration-design.md)

**目標**: Auto Chat MakerシステムとMCPサーバーの詳細連携実装

**実装内容**:
```
Day 1-2: MCPクライアントの詳細実装
- HTTP通信の実装
- エラーハンドリングの実装
- リトライ機能の実装
- ログ出力の実装

実装ファイル:
- infrastructure/external/mcp_client.py: 完全なMCPクライアント実装
- infrastructure/external/retry_handler.py: リトライ機能
- utils/logger.py: 詳細ログ出力

Day 3-4: Azure AD認証の詳細実装
- OAuth2認証フローの実装
- トークン管理の実装
- 認証ミドルウェアの実装
- セッション管理の実装

実装ファイル:
- infrastructure/auth/azure_ad.py: 完全なAzure AD認証
- infrastructure/auth/middleware.py: 認証ミドルウェア
- api/routes/auth.py: 認証フローエンドポイント

Day 5: Webhookサブスクリプション管理の実装
- サブスクリプション作成・更新
- 定期更新処理の実装
- サブスクリプション状態監視
- エラーハンドリングの強化

実装ファイル:
- application/use_cases/webhook_manager.py: Webhook管理ユースケース
- application/services/subscription_service.py: サブスクリプション管理
- domain/models/subscription.py: サブスクリプションエンティティ
```

### Phase 2: コア機能実装（2-3週間）

> **詳細設計書**: [Phase 2 コア機能設計](../design/phase2-core-functionality-design.md)

#### Week 6: AI機能実装
**目標**: Claude API連携とAI判定・生成機能の実装

**実装内容**:
```
Day 1-2: Claude API連携の実装
- Claude APIクライアントの実装
- API認証の実装
- 基本的なAPI呼び出しテスト

実装ファイル:
- infrastructure/external/claude_client.py: Claude APIクライアント
- application/services/ai_service.py: AI判定・生成サービス

Day 3-4: 返信要否判断ロジックの実装
- プロンプト設計
- AI判定ロジックの実装
- 判定結果の処理

実装ファイル:
- application/use_cases/message_processor.py: メッセージ処理ユースケース
- domain/models/reply_suggestion.py: 返信案エンティティ

Day 5: 返信案生成ロジックの実装
- 返信案生成プロンプトの設計
- 複数案生成ロジックの実装
- 生成結果の品質管理

実装ファイル:
- application/use_cases/reply_generator.py: 返信案生成ユースケース
- application/use_cases/reply_sender.py: 返信送信ユースケース
```

#### Week 7: Webhook処理実装
**目標**: Webhook受信処理とTeamsプラグインの実装

**実装内容**:
```
Day 1-2: Microsoft Graph Webhook受信エンドポイント
- Webhook受信エンドポイントの実装
- Webhook検証ロジックの実装
- MCP経由でのメッセージ取得実装
- 基本的なメッセージ処理

実装ファイル:
- api/routes/webhook.py: 完全なWebhook処理
- application/use_cases/webhook_processor.py: Webhook処理ユースケース

Day 3-4: メッセージ処理の統合
- Teamsプラグインの実装
- AI機能との統合
- エラーハンドリングの強化
- ログ出力の改善

実装ファイル:
- infrastructure/plugins/teams_plugin.py: Teamsプラグイン実装
- application/use_cases/message_processor.py: 統合メッセージ処理

Day 5: Webhook処理のテスト
- 全機能の統合テスト
- エラーケースのテスト
- パフォーマンステスト
- ドキュメントの更新
```

#### Week 8: 機能改善・最適化
**目標**: AI機能とWebhook処理の改善

**実装内容**:
```
Day 1-2: AI機能の改善
- プロンプトの最適化
- 生成品質の向上
- エラーハンドリングの改善

Day 3-4: Webhook処理の改善
- 処理速度の最適化
- エラー処理の強化
- ログ出力の改善

Day 5: 全機能の統合テスト
- エンドツーエンドテスト
- パフォーマンステスト
- ドキュメントの更新
```

### Phase 3: データ管理・UI（1-2週間）

> **詳細設計書**: [Phase 3 データ・UI設計](../design/phase3-data-ui-design.md)

#### Week 9: データベース実装
**目標**: SQLiteデータベースとリポジトリの実装

**実装内容**:
```
Day 1-2: SQLiteデータベース設計
- データベーススキーマ設計
- SQLAlchemyモデルの実装
- 基本的なCRUD操作

実装ファイル:
- infrastructure/database/models.py: SQLAlchemyモデル
- infrastructure/database/repositories.py: リポジトリ実装
- infrastructure/database/migrations/: Alembicマイグレーション

Day 3-4: データ管理機能の実装
- メッセージ履歴の管理
- 返信案履歴の管理
- データベースマイグレーション

Day 5: データベース機能のテスト
- CRUD操作のテスト
- データ整合性のテスト
- パフォーマンステスト
```

#### Week 10: Web UI実装
**目標**: シンプルなWeb UIと返信案選択・送信機能の実装

**実装内容**:
```
Day 1-2: シンプルなWeb UI実装
- FastAPIテンプレート機能の活用
- 基本的なHTML/CSS実装
- 返信案表示UI

実装ファイル:
- templates/base.html: ベーステンプレート
- templates/chat_list.html: チャット一覧
- templates/reply_suggestions.html: 返信案表示
- api/routes/ui.py: UIエンドポイント

Day 3-4: 返信案選択・送信機能
- 返信案選択ロジック
- MCP経由での返信送信
- 送信結果の確認

実装ファイル:
- api/routes/chat.py: チャット管理API
- application/use_cases/reply_sender.py: 返信送信ユースケース

Day 5: Web UIのテスト
- UI機能のテスト
- ユーザビリティテスト
- エラーケースのテスト
```

### Phase 4: 統合・テスト（1週間）

#### Week 11: 最終統合・テスト
**目標**: エンドツーエンドの動作確認と品質向上

**実装内容**:
```
Day 1-2: エンドツーエンドテスト
- 全機能の統合テスト
- エラーケースのテスト
- パフォーマンステスト

Day 3-4: エラーハンドリング改善
- エラー処理の強化
- ユーザーフレンドリーなエラーメッセージ
- ログ出力の改善

Day 5: ドキュメント整備
- API仕様書の更新
- ユーザーマニュアルの作成
- 開発者ガイドの整備
```

## 実装優先度と依存関係

### 高優先度（基盤）
- **Phase 1**: プロジェクト基盤、Azure AD認証
- **Phase 1.5**: MCPサーバー開発（必須）
- **Phase 1.6**: MCP連携実装（必須）

### 中優先度（コア機能）
- **Phase 2**: AI機能、Webhook処理
- **Phase 3**: データベース、Web UI

### 低優先度（最適化）
- **Phase 4**: 統合テスト、ドキュメント整備

## リスク管理

### 技術的リスク
- **MCPサーバー開発の複雑性**: 段階的実装と十分なテストで対応
- **Graph API制限**: レート制限とクォータ管理の実装
- **認証の複雑性**: OAuth2フローの適切な実装

### スケジュールリスク
- **MCPサーバー開発の遅延**: 2-3週間のバッファを設定
- **統合テストの複雑性**: 早期からの統合テスト実施

## 更新履歴

- 初版作成: 2024年12月
- MCPサーバー開発追加: 2024年12月 - Phase 1.5としてMCPサーバー開発を追加
- フェーズ再編成: 2024年12月 - Phase 1.6を追加し、全フェーズを再編成
- 最終更新: 2024年12月
- 更新者: 開発チーム
