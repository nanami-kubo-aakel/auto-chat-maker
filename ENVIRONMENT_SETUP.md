# 環境変数設定ガイド

## 概要

Auto Chat Makerシステムを実行するために必要な環境変数の設定方法を説明します。

## .envファイルの作成

プロジェクトルートに`.env`ファイルを作成し、以下の設定を追加してください：

```bash
# アプリケーション基本設定
APP_NAME=Auto Chat Maker
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here

# サーバー設定
HOST=0.0.0.0
PORT=8000

# データベース設定
DATABASE_URL=sqlite:///./auto_chat_maker.db
DATABASE_ECHO=false

# Azure AD認証設定
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_AUTHORITY=https://login.microsoftonline.com
AZURE_SCOPES=Chat.ReadWrite,User.Read
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback
AZURE_TOKEN_CACHE_FILE=.token_cache.json
AZURE_SESSION_SECRET=your-session-secret-here

# Claude API設定
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_API_BASE_URL=https://api.anthropic.com
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.7

# MCPサーバー設定
MCP_SERVER_URL=http://localhost:3000
MCP_API_KEY=your-mcp-api-key
MCP_SERVER_NAME=ms-365-mcp-server
MCP_SERVER_VERSION=1.0.0
MCP_CONNECTION_TIMEOUT=30
MCP_MAX_RETRIES=3

# Webhook設定
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_ENDPOINT=/api/webhook/microsoft-graph
WEBHOOK_TIMEOUT=10
WEBHOOK_SUBSCRIPTION_EXPIRATION=3600

# 返信生成設定
REPLY_GENERATION_BATCH_SIZE=10
REPLY_GENERATION_INTERVAL=300
REPLY_QUALITY_THRESHOLD=0.8
MAX_REPLY_SUGGESTIONS=3

# 機能フラグ
ENABLE_TEAMS_PLUGIN=true
ENABLE_MAIL_PLUGIN=false
ENABLE_AI_PROCESSING=true
ENABLE_WEBHOOK_PROCESSING=true
```

## 必須設定項目

### 1. Azure AD認証設定
- `AZURE_CLIENT_ID`: Azure ADアプリケーションのクライアントID
- `AZURE_CLIENT_SECRET`: Azure ADアプリケーションのクライアントシークレット
- `AZURE_TENANT_ID`: Azure ADテナントID

### 2. Claude API設定
- `CLAUDE_API_KEY`: Anthropic Claude APIのAPIキー

### 3. MCPサーバー設定
- `MCP_SERVER_URL`: MCPサーバーのURL
- `MCP_API_KEY`: MCPサーバーのAPIキー

### 4. セキュリティ設定
- `SECRET_KEY`: アプリケーションの秘密鍵
- `WEBHOOK_SECRET`: Webhook検証用の秘密鍵

## 開発環境での推奨設定

開発環境では以下の設定を推奨します：

```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_ECHO=true
```

## 本番環境での推奨設定

本番環境では以下の設定を推奨します：

```bash
DEBUG=false
LOG_LEVEL=INFO
DATABASE_ECHO=false
```

## 設定の確認

アプリケーション起動時に設定が正しく読み込まれているか確認できます：

```bash
# ヘルスチェックエンドポイントで設定を確認
curl http://localhost:8000/api/health/detailed
```

## トラブルシューティング

### 設定が読み込まれない場合
1. `.env`ファイルがプロジェクトルートに配置されているか確認
2. ファイルの文字エンコーディングがUTF-8になっているか確認
3. 環境変数名が正しく記述されているか確認

### 認証エラーが発生する場合
1. Azure AD設定が正しく設定されているか確認
2. Claude APIキーが有効か確認
3. MCPサーバーが起動しているか確認
