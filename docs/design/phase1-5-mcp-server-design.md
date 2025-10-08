# Phase 1.5: MCPサーバー開発 - 詳細設計書

## 概要

Microsoft Teams用MCPサーバー（`ms-365-mcp-server`）の詳細設計を定義します。このサーバーは、Auto Chat MakerシステムとMicrosoft Graph APIの中継役として機能し、Teamsチャットのメッセージ取得・送信を統一的に扱います。

## 設計方針

### MCPサーバー設計原則
- **MCPプロトコル準拠**: Model Context Protocolの仕様に完全準拠
- **HTTP/HTTPS通信**: RESTful APIによる統一された通信方式
- **セキュリティ重視**: OAuth2認証、HTTPS通信、レート制限
- **拡張性**: 将来的なOutlookメール対応も考慮した設計

### 技術スタック
- **言語**: Python 3.8以上
- **Webフレームワーク**: FastAPI
- **認証**: OAuth2（Azure AD）
- **通信**: HTTP/HTTPS
- **データ形式**: JSON

## 1. MCPサーバーアーキテクチャ

### 1.1 システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auto Chat     │    │   MCP Server    │    │ Microsoft Graph │
│     Maker       │◄──►│  (ms-365-mcp)   │◄──►│      API        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Microsoft     │
                       │     Teams       │
                       └─────────────────┘
```

### 1.2 ディレクトリ構造

```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーション
│   ├── config/                    # 設定管理
│   │   ├── __init__.py
│   │   ├── settings.py           # 基本設定
│   │   └── azure_settings.py     # Azure AD設定
│   ├── protocol/                  # MCPプロトコル
│   │   ├── __init__.py
│   │   ├── mcp_protocol.py       # MCPプロトコル実装
│   │   └── message_types.py      # メッセージ型定義
│   ├── server/                    # サーバー基盤
│   │   ├── __init__.py
│   │   ├── mcp_server.py         # MCPサーバー基盤
│   │   └── middleware.py         # ミドルウェア
│   ├── api/                       # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── endpoints.py          # 基本エンドポイント
│   │   ├── chat_endpoints.py     # チャットエンドポイント
│   │   └── webhook_endpoints.py  # Webhookエンドポイント
│   ├── clients/                   # 外部APIクライアント
│   │   ├── __init__.py
│   │   ├── graph_client.py       # Graph APIクライアント
│   │   └── auth_client.py        # 認証クライアント
│   ├── services/                  # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── teams_service.py      # Teams操作サービス
│   │   ├── chat_service.py       # チャット操作サービス
│   │   └── webhook_service.py    # Webhook管理サービス
│   ├── models/                    # データモデル
│   │   ├── __init__.py
│   │   ├── chat_message.py       # チャットメッセージモデル
│   │   ├── subscription.py       # サブスクリプションモデル
│   │   └── user.py               # ユーザーモデル
│   ├── auth/                      # 認証・認可
│   │   ├── __init__.py
│   │   ├── oauth2_handler.py     # OAuth2認証ハンドラー
│   │   ├── token_manager.py      # トークン管理
│   │   └── middleware.py         # 認証ミドルウェア
│   ├── security/                  # セキュリティ
│   │   ├── __init__.py
│   │   ├── rate_limiter.py       # レート制限
│   │   ├── ssl_handler.py        # SSL処理
│   │   └── validator.py          # 入力検証
│   └── utils/                     # ユーティリティ
│       ├── __init__.py
│       ├── logger.py             # ログ機能
│       ├── exceptions.py         # カスタム例外
│       └── helpers.py            # ヘルパー関数
├── tests/                         # テスト
│   ├── __init__.py
│   ├── test_protocol.py          # プロトコルテスト
│   ├── test_services.py          # サービステスト
│   └── test_integration.py       # 統合テスト
├── docs/                          # ドキュメント
│   ├── api_spec.md               # API仕様書
│   ├── deployment.md             # デプロイ手順
│   └── troubleshooting.md        # トラブルシューティング
├── requirements.txt               # 依存関係
├── Dockerfile                     # Docker設定
├── docker-compose.yml            # Docker Compose設定
└── README.md                     # プロジェクト概要
```

## 2. MCPプロトコル実装

### 2.1 プロトコル基盤

#### `src/protocol/mcp_protocol.py`
```python
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel


class MCPMessageType(Enum):
    """MCPメッセージタイプ"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPRequest(BaseModel):
    """MCPリクエストモデル"""
    id: str
    method: str
    params: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"


class MCPResponse(BaseModel):
    """MCPレスポンスモデル"""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"


class MCPProtocol:
    """MCPプロトコル実装"""

    def __init__(self):
        self.supported_methods = {
            "chat.get_message": self.get_chat_message,
            "chat.send_message": self.send_chat_message,
            "chat.get_thread": self.get_chat_thread,
            "webhook.create_subscription": self.create_subscription,
            "webhook.renew_subscription": self.renew_subscription,
            "user.get_info": self.get_user_info
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """リクエストを処理"""
        try:
            if request.method not in self.supported_methods:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method not found: {request.method}"
                    }
                )

            handler = self.supported_methods[request.method]
            result = await handler(request.params or {})

            return MCPResponse(
                id=request.id,
                result=result
            )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )

    async def get_chat_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """チャットメッセージ取得"""
        message_id = params.get("message_id")
        if not message_id:
            raise ValueError("message_id is required")

        # Teamsサービスを呼び出し
        return await self.teams_service.get_message(message_id)

    async def send_chat_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """チャットメッセージ送信"""
        message_id = params.get("message_id")
        content = params.get("content")

        if not message_id or not content:
            raise ValueError("message_id and content are required")

        # Teamsサービスを呼び出し
        return await self.teams_service.send_message(message_id, content)
```

### 2.2 メッセージ型定義

#### `src/protocol/message_types.py`
```python
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    """チャットメッセージモデル"""
    id: str
    content: str
    sender: str
    sent_at: datetime
    thread_id: Optional[str] = None
    channel_id: Optional[str] = None
    team_id: Optional[str] = None
    message_type: str = "text"


class ChatThread(BaseModel):
    """チャットスレッドモデル"""
    id: str
    title: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime


class Subscription(BaseModel):
    """サブスクリプションモデル"""
    id: str
    resource: str
    change_type: str
    notification_url: str
    expiration_datetime: datetime
    client_state: Optional[str] = None


class UserInfo(BaseModel):
    """ユーザー情報モデル"""
    id: str
    display_name: str
    email: str
    photo_url: Optional[str] = None
```

## 3. サーバー基盤実装

### 3.1 MCPサーバー基盤

#### `src/server/mcp_server.py`
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import uvicorn

from ..protocol.mcp_protocol import MCPProtocol, MCPRequest, MCPResponse
from ..auth.middleware import verify_token
from ..utils.logger import get_logger


class MCPServer:
    """MCPサーバー基盤"""

    def __init__(self):
        self.app = FastAPI(
            title="Microsoft 365 MCP Server",
            description="MCP server for Microsoft Teams integration",
            version="1.0.0"
        )
        self.protocol = MCPProtocol()
        self.logger = get_logger(__name__)
        self.security = HTTPBearer()

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """ミドルウェアの設定"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """ルートの設定"""

        @self.app.post("/mcp")
        async def handle_mcp_request(
            request: Dict[str, Any],
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """MCPリクエスト処理"""
            try:
                # トークン検証
                await verify_token(credentials.credentials)

                # MCPリクエストの処理
                mcp_request = MCPRequest(**request)
                response = await self.protocol.handle_request(mcp_request)

                self.logger.info(
                    f"MCP request processed: {mcp_request.method}",
                    request_id=mcp_request.id
                )

                return response.dict()

            except Exception as e:
                self.logger.error(f"MCP request failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            """ヘルスチェック"""
            return {"status": "healthy", "service": "mcp-server"}

    def run(self, host: str = "0.0.0.0", port: int = 3000):
        """サーバー起動"""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
```

### 3.2 認証ミドルウェア

#### `src/auth/middleware.py`
```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime

from ..config.azure_settings import AzureSettings
from ..utils.logger import get_logger


class AuthMiddleware:
    """認証ミドルウェア"""

    def __init__(self):
        self.settings = AzureSettings()
        self.logger = get_logger(__name__)

    async def verify_token(self, token: str) -> bool:
        """トークンの検証"""
        try:
            # JWTトークンの検証
            payload = jwt.decode(
                token,
                self.settings.azure_client_secret,
                algorithms=["HS256"]
            )

            # 有効期限のチェック
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")

            return True

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            self.logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """現在のユーザー取得"""
        await self.verify_token(credentials.credentials)
        return credentials.credentials
```

## 4. Microsoft Graph API連携

### 4.1 Graph APIクライアント

#### `src/clients/graph_client.py`
```python
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

from ..config.azure_settings import AzureSettings
from ..auth.token_manager import TokenManager
from ..utils.logger import get_logger


class GraphClient:
    """Microsoft Graph APIクライアント"""

    def __init__(self):
        self.settings = AzureSettings()
        self.token_manager = TokenManager()
        self.logger = get_logger(__name__)
        self.base_url = "https://graph.microsoft.com/v1.0"

    async def _get_headers(self) -> Dict[str, str]:
        """認証ヘッダーを取得"""
        token = await self.token_manager.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """HTTPリクエストを実行"""
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_headers()

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # トークン更新を試行
                    await self.token_manager.refresh_token()
                    headers = await self._get_headers()
                    async with session.request(
                        method, url, headers=headers, json=data
                    ) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            raise Exception(f"Graph API error: {retry_response.status}")
                else:
                    raise Exception(f"Graph API error: {response.status}")

    async def get_chat_message(self, message_id: str) -> Dict[str, Any]:
        """チャットメッセージを取得"""
        endpoint = f"/chats/messages/{message_id}"
        return await self._make_request("GET", endpoint)

    async def send_chat_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """チャットメッセージを送信"""
        endpoint = f"/chats/{chat_id}/messages"
        data = {
            "body": {
                "content": content,
                "contentType": "text"
            }
        }
        return await self._make_request("POST", endpoint, data)

    async def get_chat_thread(self, thread_id: str) -> Dict[str, Any]:
        """チャットスレッドを取得"""
        endpoint = f"/chats/{thread_id}"
        return await self._make_request("GET", endpoint)

    async def create_subscription(
        self,
        resource: str,
        change_type: str,
        notification_url: str,
        expiration_datetime: datetime
    ) -> Dict[str, Any]:
        """サブスクリプションを作成"""
        endpoint = "/subscriptions"
        data = {
            "resource": resource,
            "changeType": change_type,
            "notificationUrl": notification_url,
            "expirationDateTime": expiration_datetime.isoformat(),
            "clientState": "mcp-server-subscription"
        }
        return await self._make_request("POST", endpoint, data)

    async def renew_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """サブスクリプションを更新"""
        endpoint = f"/subscriptions/{subscription_id}"
        data = {
            "expirationDateTime": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        return await self._make_request("PATCH", endpoint, data)
```

### 4.2 Teams操作サービス

#### `src/services/teams_service.py`
```python
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..clients.graph_client import GraphClient
from ..models.chat_message import ChatMessage
from ..models.chat_thread import ChatThread
from ..utils.logger import get_logger


class TeamsService:
    """Teams操作サービス"""

    def __init__(self):
        self.graph_client = GraphClient()
        self.logger = get_logger(__name__)

    async def get_message(self, message_id: str) -> ChatMessage:
        """メッセージを取得"""
        try:
            graph_data = await self.graph_client.get_chat_message(message_id)

            return ChatMessage(
                id=graph_data["id"],
                content=graph_data["body"]["content"],
                sender=graph_data["from"]["user"]["displayName"],
                sent_at=datetime.fromisoformat(graph_data["createdDateTime"].replace("Z", "+00:00")),
                thread_id=graph_data.get("replyToId"),
                channel_id=graph_data.get("channelId"),
                team_id=graph_data.get("teamId"),
                message_type=graph_data.get("body", {}).get("contentType", "text")
            )
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            raise

    async def send_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """メッセージを送信"""
        try:
            result = await self.graph_client.send_chat_message(chat_id, content)

            self.logger.info(
                f"Message sent to chat {chat_id}",
                message_id=result["id"]
            )

            return {
                "success": True,
                "message_id": result["id"],
                "sent_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to send message to chat {chat_id}: {e}")
            raise

    async def get_thread(self, thread_id: str) -> ChatThread:
        """スレッドを取得"""
        try:
            graph_data = await self.graph_client.get_chat_thread(thread_id)

            messages = []
            for msg_data in graph_data.get("messages", []):
                messages.append(ChatMessage(
                    id=msg_data["id"],
                    content=msg_data["body"]["content"],
                    sender=msg_data["from"]["user"]["displayName"],
                    sent_at=datetime.fromisoformat(msg_data["createdDateTime"].replace("Z", "+00:00")),
                    thread_id=thread_id
                ))

            return ChatThread(
                id=thread_id,
                title=graph_data.get("topic"),
                messages=messages,
                created_at=datetime.fromisoformat(graph_data["createdDateTime"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(graph_data["lastUpdatedDateTime"].replace("Z", "+00:00"))
            )
        except Exception as e:
            self.logger.error(f"Failed to get thread {thread_id}: {e}")
            raise
```

## 5. Webhook管理機能

### 5.1 Webhook管理サービス

#### `src/services/webhook_service.py`
```python
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..clients.graph_client import GraphClient
from ..models.subscription import Subscription
from ..utils.logger import get_logger


class WebhookService:
    """Webhook管理サービス"""

    def __init__(self):
        self.graph_client = GraphClient()
        self.logger = get_logger(__name__)

    async def create_subscription(
        self,
        resource: str,
        change_type: str,
        notification_url: str,
        expiration_hours: int = 1
    ) -> Subscription:
        """サブスクリプションを作成"""
        try:
            expiration_datetime = datetime.utcnow() + timedelta(hours=expiration_hours)

            graph_data = await self.graph_client.create_subscription(
                resource=resource,
                change_type=change_type,
                notification_url=notification_url,
                expiration_datetime=expiration_datetime
            )

            subscription = Subscription(
                id=graph_data["id"],
                resource=graph_data["resource"],
                change_type=graph_data["changeType"],
                notification_url=graph_data["notificationUrl"],
                expiration_datetime=datetime.fromisoformat(graph_data["expirationDateTime"].replace("Z", "+00:00")),
                client_state=graph_data.get("clientState")
            )

            self.logger.info(
                f"Subscription created: {subscription.id}",
                resource=resource,
                expiration=expiration_datetime
            )

            return subscription

        except Exception as e:
            self.logger.error(f"Failed to create subscription: {e}")
            raise

    async def renew_subscription(self, subscription_id: str) -> bool:
        """サブスクリプションを更新"""
        try:
            await self.graph_client.renew_subscription(subscription_id)

            self.logger.info(f"Subscription renewed: {subscription_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to renew subscription {subscription_id}: {e}")
            return False

    async def handle_webhook_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Webhook通知を処理"""
        try:
            for value in notification_data.get("value", []):
                subscription_id = value.get("subscriptionId")
                resource = value.get("resource")
                change_type = value.get("changeType")

                self.logger.info(
                    f"Webhook notification received",
                    subscription_id=subscription_id,
                    resource=resource,
                    change_type=change_type
                )

                # 通知処理の実装（Auto Chat Makerへの転送など）
                await self._process_notification(value)

            return True

        except Exception as e:
            self.logger.error(f"Failed to handle webhook notification: {e}")
            return False

    async def _process_notification(self, notification: Dict[str, Any]):
        """通知の処理"""
        # Auto Chat Makerシステムへの通知転送
        # この部分はAuto Chat Makerとの連携で実装
        pass
```

## 6. セキュリティ実装

### 6.1 レート制限

#### `src/security/rate_limiter.py`
```python
import time
from typing import Dict, Tuple
from collections import defaultdict
import asyncio

from ..utils.logger import get_logger


class RateLimiter:
    """レート制限実装"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.logger = get_logger(__name__)

    async def check_rate_limit(self, client_id: str) -> bool:
        """レート制限チェック"""
        current_time = time.time()

        # 古いリクエストを削除
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window_seconds
        ]

        # リクエスト数チェック
        if len(self.requests[client_id]) >= self.max_requests:
            self.logger.warning(
                f"Rate limit exceeded for client: {client_id}",
                requests=len(self.requests[client_id]),
                max_requests=self.max_requests
            )
            return False

        # 新しいリクエストを追加
        self.requests[client_id].append(current_time)
        return True

    async def wait_if_needed(self, client_id: str):
        """必要に応じて待機"""
        while not await self.check_rate_limit(client_id):
            await asyncio.sleep(1)
```

### 6.2 SSL処理

#### `src/security/ssl_handler.py`
```python
import ssl
from typing import Optional
from pathlib import Path

from ..utils.logger import get_logger


class SSLHandler:
    """SSL処理"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def create_ssl_context(
        self,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None
    ) -> Optional[ssl.SSLContext]:
        """SSLコンテキストを作成"""
        if not cert_file or not key_file:
            self.logger.warning("SSL certificates not provided, using HTTP")
            return None

        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)

            self.logger.info("SSL context created successfully")
            return ssl_context

        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {e}")
            return None

    def validate_certificates(self, cert_file: str, key_file: str) -> bool:
        """証明書の検証"""
        try:
            cert_path = Path(cert_file)
            key_path = Path(key_file)

            if not cert_path.exists():
                self.logger.error(f"Certificate file not found: {cert_file}")
                return False

            if not key_path.exists():
                self.logger.error(f"Key file not found: {key_file}")
                return False

            self.logger.info("SSL certificates validated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Certificate validation failed: {e}")
            return False
```

## 7. 設定管理

### 7.1 基本設定

#### `src/config/settings.py`
```python
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCPサーバー基本設定"""

    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 3000
    debug: bool = False
    log_level: str = "INFO"

    # MCP設定
    mcp_server_name: str = "ms-365-mcp-server"
    mcp_server_version: str = "1.0.0"
    mcp_server_description: str = "Microsoft 365 MCP Server"

    # セキュリティ設定
    rate_limit_max_requests: int = 100
    rate_limit_window_seconds: int = 60
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None

    # ログ設定
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = False
```

### 7.2 Azure AD設定

#### `src/config/azure_settings.py`
```python
from typing import List
from pydantic_settings import BaseSettings


class AzureSettings(BaseSettings):
    """Azure AD設定"""

    # Azure AD設定
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str

    # Graph API設定
    graph_api_url: str = "https://graph.microsoft.com/v1.0"
    graph_api_scopes: List[str] = [
        "https://graph.microsoft.com/.default"
    ]

    # 認証設定
    auth_authority: str = "https://login.microsoftonline.com"
    token_cache_file: str = ".token_cache.json"

    # Webhook設定
    webhook_secret: Optional[str] = None
    webhook_timeout: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "AZURE_"
```

## 8. メインアプリケーション

### 8.1 アプリケーション起動

#### `src/main.py`
```python
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .server.mcp_server import MCPServer
from .config.settings import Settings
from .utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時の処理
    setup_logging()
    yield
    # 終了時の処理


def create_app() -> FastAPI:
    """FastAPIアプリケーションを作成"""
    settings = Settings()

    app = FastAPI(
        title=settings.mcp_server_name,
        description=settings.mcp_server_description,
        version=settings.mcp_server_version,
        lifespan=lifespan
    )

    # MCPサーバーの設定
    mcp_server = MCPServer()
    app.mount("/mcp", mcp_server.app)

    return app


def main():
    """メイン関数"""
    settings = Settings()

    uvicorn.run(
        "src.main:create_app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
```

## 9. テスト実装

### 9.1 プロトコルテスト

#### `tests/test_protocol.py`
```python
import pytest
from unittest.mock import AsyncMock, patch

from src.protocol.mcp_protocol import MCPProtocol, MCPRequest, MCPResponse


class TestMCPProtocol:
    """MCPプロトコルテスト"""

    @pytest.fixture
    def protocol(self):
        return MCPProtocol()

    @pytest.mark.asyncio
    async def test_handle_request_success(self, protocol):
        """正常なリクエスト処理テスト"""
        request = MCPRequest(
            id="test-1",
            method="chat.get_message",
            params={"message_id": "msg-123"}
        )

        with patch.object(protocol, 'get_chat_message', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"content": "test message"}

            response = await protocol.handle_request(request)

            assert response.id == "test-1"
            assert response.result == {"content": "test message"}
            assert response.error is None

    @pytest.mark.asyncio
    async def test_handle_request_method_not_found(self, protocol):
        """存在しないメソッドのテスト"""
        request = MCPRequest(
            id="test-2",
            method="unknown.method",
            params={}
        )

        response = await protocol.handle_request(request)

        assert response.id == "test-2"
        assert response.error is not None
        assert response.error["code"] == -32601

    @pytest.mark.asyncio
    async def test_handle_request_internal_error(self, protocol):
        """内部エラーのテスト"""
        request = MCPRequest(
            id="test-3",
            method="chat.get_message",
            params={"message_id": "msg-123"}
        )

        with patch.object(protocol, 'get_chat_message', side_effect=Exception("Test error")):
            response = await protocol.handle_request(request)

            assert response.id == "test-3"
            assert response.error is not None
            assert response.error["code"] == -32603
```

## 10. デプロイ設定

### 10.1 Docker設定

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY src/ ./src/

# 設定ファイルのコピー
COPY .env .env

# ポートの公開
EXPOSE 3000

# アプリケーション起動
CMD ["python", "-m", "src.main"]
```

### 10.2 Docker Compose設定

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "3000:3000"
    environment:
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## 更新履歴

- 初版作成: 2024年12月
- MCPプロトコル実装: 2024年12月 - MCPプロトコルの詳細実装
- Graph API連携: 2024年12月 - Microsoft Graph APIとの連携実装
- セキュリティ機能: 2024年12月 - レート制限、SSL処理の実装
- 最終更新: 2024年12月
- 更新者: 開発チーム
