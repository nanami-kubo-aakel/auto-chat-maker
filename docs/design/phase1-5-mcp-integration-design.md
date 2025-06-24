# Phase 1.5: MCP連携詳細実装 - 詳細クラス設計書

## 概要

Auto Chat MakerシステムのPhase 1.5（MCP連携詳細実装）における詳細なクラス設計を定義します。MCPサーバーとの連携、Azure AD認証、Webhook管理の詳細実装をクリーンアーキテクチャの原則に従って設計します。

## 設計方針

### MCP連携設計原則
- **HTTP通信**: MCPサーバーとのHTTP/HTTPS通信
- **エラーハンドリング**: 接続エラー、タイムアウト、リトライ機能
- **認証管理**: APIキーによる認証
- **非同期処理**: FastAPI非同期機能の活用

### Azure AD認証設計原則
- **OAuth2認証フロー**: 認証コードフロー
- **トークン管理**: アクセストークン、リフレッシュトークンの管理
- **セッション管理**: ユーザーセッションの管理
- **セキュリティ**: トークンの安全な保存

## 1. MCPクライアント実装 (infrastructure/external/)

### 1.1 MCPクライアント基盤

#### `infrastructure/external/mcp_client.py`
```python
class MCPClient:
    """MCPサーバーとの通信を管理するクライアント"""

    def __init__(self, server_url: str, api_key: str, timeout: int = 30):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = AppLogger(__name__)

    async def __aenter__(self):
        """非同期コンテキストマネージャー開始"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー終了"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """認証ヘッダーを取得"""
        return {
            "Authorization": f"Bearer {self.api_key}",
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
        if not self.session:
            raise MCPConnectionError("Client session not initialized")

        url = f"{self.server_url}{endpoint}"
        headers = self._get_headers()

        try:
            async with self.session.request(
                method, url, headers=headers, json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 404:
                    raise MCPConnectionError(f"Endpoint not found: {endpoint}")
                else:
                    raise MCPConnectionError(
                        f"MCP server error: {response.status}"
                    )
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection failed: {e}")
        except asyncio.TimeoutError:
            raise MCPConnectionError("Request timeout")

    async def get_chat_message(self, message_id: str) -> Dict[str, Any]:
        """チャットメッセージを取得"""
        endpoint = f"/mcp/ms-365/chat/{message_id}"
        return await self._make_request("GET", endpoint)

    async def send_chat_reply(self, message_id: str, content: str) -> bool:
        """チャット返信を送信"""
        endpoint = "/mcp/ms-365/chat/reply"
        data = {
            "message_id": message_id,
            "content": content
        }
        result = await self._make_request("POST", endpoint, data)
        return result.get("success", False)

    async def get_chat_thread(self, thread_id: str) -> Dict[str, Any]:
        """チャットスレッドを取得"""
        endpoint = f"/mcp/ms-365/chat/thread/{thread_id}"
        return await self._make_request("GET", endpoint)

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """ユーザー情報を取得"""
        endpoint = f"/mcp/ms-365/user/{user_id}"
        return await self._make_request("GET", endpoint)
```

**責任**:
- MCPサーバーとのHTTP通信管理
- 認証ヘッダーの管理
- エラーハンドリングとリトライ機能
- 非同期セッション管理

**依存関係**:
- `aiohttp` - HTTP通信ライブラリ
- `AppLogger` - ログ出力
- `MCPConnectionError` - カスタム例外

### 1.2 リトライ機能

#### `infrastructure/external/retry_handler.py`
```python
class RetryConfig:
    """リトライ設定クラス"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

class RetryHandler:
    """リトライ処理クラス"""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = AppLogger(__name__)

    async def execute_with_retry(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """リトライ機能付きで操作を実行"""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except (MCPConnectionError, aiohttp.ClientError) as e:
                last_exception = e

                if attempt == self.config.max_retries:
                    self.logger.error(
                        f"Max retries exceeded: {e}",
                        attempt=attempt + 1,
                        max_retries=self.config.max_retries
                    )
                    raise last_exception

                delay = min(
                    self.config.base_delay * (self.config.exponential_base ** attempt),
                    self.config.max_delay
                )

                self.logger.warning(
                    f"Retry attempt {attempt + 1}/{self.config.max_retries + 1}: {e}",
                    delay=delay
                )

                await asyncio.sleep(delay)

        raise last_exception

class MCPClientWithRetry(MCPClient):
    """リトライ機能付きMCPクライアント"""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        timeout: int = 30,
        retry_config: Optional[RetryConfig] = None
    ):
        super().__init__(server_url, api_key, timeout)
        self.retry_handler = RetryHandler(
            retry_config or RetryConfig()
        )

    async def get_chat_message_with_retry(self, message_id: str) -> Dict[str, Any]:
        """リトライ機能付きチャットメッセージ取得"""
        return await self.retry_handler.execute_with_retry(
            self.get_chat_message, message_id
        )

    async def send_chat_reply_with_retry(self, message_id: str, content: str) -> bool:
        """リトライ機能付きチャット返信送信"""
        return await self.retry_handler.execute_with_retry(
            self.send_chat_reply, message_id, content
        )
```

**責任**:
- リトライロジックの実装
- 指数バックオフ機能
- リトライ設定の管理
- エラーログの出力

**依存関係**:
- `asyncio` - 非同期処理
- `AppLogger` - ログ出力
- `MCPClient` - MCPクライアント基盤

## 2. Azure AD認証実装 (infrastructure/auth/)

### 2.1 Azure AD認証基盤

#### `infrastructure/auth/azure_ad.py`
```python
class AzureADAuth:
    """Azure AD認証クラス"""

    def __init__(self, settings: AzureSettings):
        self.settings = settings
        self.logger = AppLogger(__name__)
        self.oauth_session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.oauth_session.close()

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """認証URLを生成"""
        params = {
            "client_id": self.settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.settings.graph_api_scopes),
            "state": state,
            "response_mode": "query"
        }

        auth_url = f"https://login.microsoftonline.com/{self.settings.azure_tenant_id}/oauth2/v2.0/authorize"
        query_string = "&".join([f"{k}={quote(v)}" for k, v in params.items()])

        return f"{auth_url}?{query_string}"

    async def exchange_code_for_token(
        self,
        authorization_code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """認証コードをトークンと交換"""
        token_url = f"https://login.microsoftonline.com/{self.settings.azure_tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": self.settings.azure_client_id,
            "client_secret": self.settings.azure_client_secret,
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        try:
            async with self.oauth_session.post(token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise AuthenticationError(
                        f"Token exchange failed: {error_data.get('error_description', 'Unknown error')}"
                    )
        except aiohttp.ClientError as e:
            raise AuthenticationError(f"Token exchange request failed: {e}")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """リフレッシュトークンでアクセストークンを更新"""
        token_url = f"https://login.microsoftonline.com/{self.settings.azure_tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": self.settings.azure_client_id,
            "client_secret": self.settings.azure_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            async with self.oauth_session.post(token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise AuthenticationError(
                        f"Token refresh failed: {error_data.get('error_description', 'Unknown error')}"
                    )
        except aiohttp.ClientError as e:
            raise AuthenticationError(f"Token refresh request failed: {e}")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """ユーザー情報を取得"""
        graph_url = f"{self.settings.graph_api_url}/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with self.oauth_session.get(graph_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise AuthenticationError("Failed to get user info")
        except aiohttp.ClientError as e:
            raise AuthenticationError(f"User info request failed: {e}")
```

**責任**:
- OAuth2認証フローの実装
- 認証コードとトークンの交換
- リフレッシュトークンによるトークン更新
- ユーザー情報の取得

**依存関係**:
- `aiohttp` - HTTP通信
- `AzureSettings` - Azure設定
- `AppLogger` - ログ出力

### 2.2 トークン管理

#### `infrastructure/auth/token_manager.py`
```python
class TokenInfo:
    """トークン情報クラス"""

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        token_type: str = "Bearer"
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.token_type = token_type
        self.created_at = datetime.utcnow()

    @property
    def expires_at(self) -> datetime:
        """トークンの有効期限を取得"""
        return self.created_at + timedelta(seconds=self.expires_in)

    def is_expired(self, buffer_minutes: int = 5) -> bool:
        """トークンが期限切れかどうかチェック"""
        buffer_time = timedelta(minutes=buffer_minutes)
        return datetime.utcnow() >= (self.expires_at - buffer_time)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でトークン情報を取得"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_in": self.expires_in,
            "token_type": self.token_type,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenInfo":
        """辞書からトークン情報を作成"""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"],
            token_type=data.get("token_type", "Bearer")
        )

class TokenManager:
    """トークン管理クラス"""

    def __init__(self, azure_auth: AzureADAuth):
        self.azure_auth = azure_auth
        self.logger = AppLogger(__name__)
        self._tokens: Dict[str, TokenInfo] = {}

    def store_token(self, user_id: str, token_info: TokenInfo) -> None:
        """トークンを保存"""
        self._tokens[user_id] = token_info
        self.logger.info(f"Token stored for user: {user_id}")

    def get_token(self, user_id: str) -> Optional[TokenInfo]:
        """トークンを取得"""
        return self._tokens.get(user_id)

    def remove_token(self, user_id: str) -> None:
        """トークンを削除"""
        if user_id in self._tokens:
            del self._tokens[user_id]
            self.logger.info(f"Token removed for user: {user_id}")

    async def get_valid_token(self, user_id: str) -> Optional[str]:
        """有効なアクセストークンを取得"""
        token_info = self.get_token(user_id)
        if not token_info:
            return None

        if token_info.is_expired():
            try:
                # リフレッシュトークンでトークンを更新
                refresh_result = await self.azure_auth.refresh_access_token(
                    token_info.refresh_token
                )

                new_token_info = TokenInfo(
                    access_token=refresh_result["access_token"],
                    refresh_token=refresh_result.get("refresh_token", token_info.refresh_token),
                    expires_in=refresh_result["expires_in"],
                    token_type=refresh_result.get("token_type", "Bearer")
                )

                self.store_token(user_id, new_token_info)
                return new_token_info.access_token
            except AuthenticationError as e:
                self.logger.error(f"Token refresh failed for user {user_id}: {e}")
                self.remove_token(user_id)
                return None

        return token_info.access_token

    def is_authenticated(self, user_id: str) -> bool:
        """ユーザーが認証済みかどうかチェック"""
        token_info = self.get_token(user_id)
        return token_info is not None and not token_info.is_expired()
```

**責任**:
- トークンの保存・取得・削除
- トークンの有効期限管理
- リフレッシュトークンによる自動更新
- 認証状態の管理

**依存関係**:
- `AzureADAuth` - Azure AD認証
- `AppLogger` - ログ出力
- `datetime` - 時間管理

### 2.3 認証ミドルウェア

#### `infrastructure/auth/middleware.py`
```python
class AuthMiddleware:
    """認証ミドルウェア"""

    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.logger = AppLogger(__name__)

    async def __call__(self, request: Request, call_next):
        """ミドルウェア処理"""
        # 認証不要なパスをスキップ
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # セッションからユーザーIDを取得
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)

        # トークンの有効性をチェック
        if not self.token_manager.is_authenticated(user_id):
            # トークンが無効な場合はログインページにリダイレクト
            request.session.clear()
            return RedirectResponse(url="/auth/login", status_code=302)

        # リクエストにユーザー情報を追加
        request.state.user_id = user_id
        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """認証不要なパスかどうかチェック"""
        public_paths = [
            "/health",
            "/auth/login",
            "/auth/callback",
            "/static",
            "/docs",
            "/openapi.json"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)

class SessionMiddleware:
    """セッション管理ミドルウェア"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    async def __call__(self, request: Request, call_next):
        """セッション管理処理"""
        # セッションの初期化
        if "session" not in request.state.__dict__:
            request.state.session = {}

        response = await call_next(request)

        # セッション情報をレスポンスに設定
        if hasattr(request.state, "session") and request.state.session:
            # 実際の実装では適切なセッション管理ライブラリを使用
            pass

        return response
```

**責任**:
- 認証状態のチェック
- セッション管理
- 認証不要パスの管理
- リダイレクト処理

**依存関係**:
- `TokenManager` - トークン管理
- `AppLogger` - ログ出力
- `FastAPI` - Webフレームワーク

## 3. Webhook管理実装 (application/use_cases/)

### 3.1 Webhook管理ユースケース

#### `application/use_cases/webhook_manager.py`
```python
class WebhookManager:
    """Webhook管理ユースケース"""

    def __init__(
        self,
        graph_client: "GraphClient",
        subscription_repository: "SubscriptionRepository",
        logger: AppLogger
    ):
        self.graph_client = graph_client
        self.subscription_repository = subscription_repository
        self.logger = logger

    async def create_subscription(
        self,
        user_id: str,
        resource: str,
        webhook_url: str,
        change_type: str = "created"
    ) -> "Subscription":
        """Webhookサブスクリプションを作成"""
        try:
            # Microsoft Graph APIでサブスクリプションを作成
            subscription_data = await self.graph_client.create_subscription(
                resource=resource,
                change_type=change_type,
                webhook_url=webhook_url
            )

            # データベースにサブスクリプション情報を保存
            subscription = Subscription(
                user_id=user_id,
                subscription_id=subscription_data["id"],
                resource=resource,
                resource_type="teams_chat",
                expires_at=datetime.fromisoformat(subscription_data["expirationDateTime"]),
                webhook_url=webhook_url,
                change_type=change_type
            )

            saved_subscription = await self.subscription_repository.save(subscription)
            self.logger.info(
                f"Webhook subscription created: {saved_subscription.id}",
                user_id=user_id,
                resource=resource
            )

            return saved_subscription

        except Exception as e:
            self.logger.error(
                f"Failed to create webhook subscription: {e}",
                user_id=user_id,
                resource=resource
            )
            raise

    async def renew_subscription(self, subscription_id: str) -> "Subscription":
        """Webhookサブスクリプションを更新"""
        try:
            # データベースからサブスクリプション情報を取得
            subscription = await self.subscription_repository.find_by_id(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")

            # Microsoft Graph APIでサブスクリプションを更新
            updated_data = await self.graph_client.renew_subscription(
                subscription_id=subscription.subscription_id
            )

            # データベースのサブスクリプション情報を更新
            subscription.expires_at = datetime.fromisoformat(
                updated_data["expirationDateTime"]
            )
            subscription.updated_at = datetime.utcnow()

            updated_subscription = await self.subscription_repository.save(subscription)
            self.logger.info(
                f"Webhook subscription renewed: {subscription_id}",
                expires_at=updated_subscription.expires_at
            )

            return updated_subscription

        except Exception as e:
            self.logger.error(
                f"Failed to renew webhook subscription: {e}",
                subscription_id=subscription_id
            )
            raise

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Webhookサブスクリプションを削除"""
        try:
            # データベースからサブスクリプション情報を取得
            subscription = await self.subscription_repository.find_by_id(subscription_id)
            if not subscription:
                return False

            # Microsoft Graph APIでサブスクリプションを削除
            await self.graph_client.delete_subscription(subscription.subscription_id)

            # データベースからサブスクリプション情報を削除
            await self.subscription_repository.delete(subscription_id)

            self.logger.info(f"Webhook subscription deleted: {subscription_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to delete webhook subscription: {e}",
                subscription_id=subscription_id
            )
            raise

    async def get_expired_subscriptions(self) -> List["Subscription"]:
        """期限切れサブスクリプションを取得"""
        return await self.subscription_repository.find_expired()

    async def cleanup_expired_subscriptions(self) -> int:
        """期限切れサブスクリプションをクリーンアップ"""
        expired_subscriptions = await self.get_expired_subscriptions()
        cleaned_count = 0

        for subscription in expired_subscriptions:
            try:
                await self.delete_subscription(subscription.id)
                cleaned_count += 1
            except Exception as e:
                self.logger.error(
                    f"Failed to cleanup expired subscription: {e}",
                    subscription_id=subscription.id
                )

        self.logger.info(
            f"Cleaned up {cleaned_count} expired subscriptions",
            total_expired=len(expired_subscriptions),
            cleaned_count=cleaned_count
        )

        return cleaned_count
```

**責任**:
- Webhookサブスクリプションの作成・更新・削除
- 期限切れサブスクリプションの管理
- Microsoft Graph APIとの連携
- データベースとの同期

**依存関係**:
- `GraphClient` - Graph APIクライアント
- `SubscriptionRepository` - サブスクリプションリポジトリ
- `AppLogger` - ログ出力

### 3.2 サブスクリプション管理サービス

#### `application/services/subscription_service.py`
```python
class SubscriptionService:
    """サブスクリプション管理サービス"""

    def __init__(
        self,
        webhook_manager: WebhookManager,
        logger: AppLogger
    ):
        self.webhook_manager = webhook_manager
        self.logger = logger

    async def setup_user_subscriptions(self, user_id: str) -> List["Subscription"]:
        """ユーザーのサブスクリプションを設定"""
        try:
            # Teamsチャットのサブスクリプションを作成
            webhook_url = f"https://your-app.ngrok.io/api/webhook/microsoft-graph"

            # 複数のリソースに対してサブスクリプションを作成
            subscriptions = []

            # チャットメッセージのサブスクリプション
            chat_subscription = await self.webhook_manager.create_subscription(
                user_id=user_id,
                resource="/teams/{team-id}/channels/{channel-id}/messages",
                webhook_url=webhook_url,
                change_type="created"
            )
            subscriptions.append(chat_subscription)

            # チームメッセージのサブスクリプション
            team_subscription = await self.webhook_manager.create_subscription(
                user_id=user_id,
                resource="/teams/{team-id}/messages",
                webhook_url=webhook_url,
                change_type="created"
            )
            subscriptions.append(team_subscription)

            self.logger.info(
                f"User subscriptions setup completed: {len(subscriptions)} subscriptions",
                user_id=user_id
            )

            return subscriptions

        except Exception as e:
            self.logger.error(
                f"Failed to setup user subscriptions: {e}",
                user_id=user_id
            )
            raise

    async def renew_all_subscriptions(self) -> int:
        """全サブスクリプションを更新"""
        try:
            # 期限切れに近いサブスクリプションを取得
            expired_subscriptions = await self.webhook_manager.get_expired_subscriptions()
            renewed_count = 0

            for subscription in expired_subscriptions:
                try:
                    await self.webhook_manager.renew_subscription(subscription.id)
                    renewed_count += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to renew subscription: {e}",
                        subscription_id=subscription.id
                    )

            self.logger.info(
                f"Subscription renewal completed: {renewed_count} renewed",
                total_expired=len(expired_subscriptions),
                renewed_count=renewed_count
            )

            return renewed_count

        except Exception as e:
            self.logger.error(f"Failed to renew subscriptions: {e}")
            raise

    async def cleanup_expired_subscriptions(self) -> int:
        """期限切れサブスクリプションをクリーンアップ"""
        return await self.webhook_manager.cleanup_expired_subscriptions()
```

**責任**:
- ユーザーサブスクリプションの一括設定
- 定期更新処理の管理
- クリーンアップ処理の管理
- エラーハンドリング

**依存関係**:
- `WebhookManager` - Webhook管理ユースケース
- `AppLogger` - ログ出力

## 4. 実装順序と依存関係

### 実装順序
1. **infrastructure/external/retry_handler.py** - リトライ機能（依存なし）
2. **infrastructure/external/mcp_client.py** - MCPクライアント基盤（リトライ機能に依存）
3. **infrastructure/auth/azure_ad.py** - Azure AD認証（MCPクライアントに依存）
4. **infrastructure/auth/token_manager.py** - トークン管理（Azure AD認証に依存）
5. **infrastructure/auth/middleware.py** - 認証ミドルウェア（トークン管理に依存）
6. **application/use_cases/webhook_manager.py** - Webhook管理（全認証基盤に依存）
7. **application/services/subscription_service.py** - サブスクリプション管理（Webhook管理に依存）

### 依存関係図
```
infrastructure/external/retry_handler.py
    ↓
infrastructure/external/mcp_client.py
    ↓
infrastructure/auth/azure_ad.py
    ↓
infrastructure/auth/token_manager.py
    ↓
infrastructure/auth/middleware.py
    ↓
application/use_cases/webhook_manager.py
    ↓
application/services/subscription_service.py
```

## 5. テスト戦略

### 単体テスト対象
- **MCPクライアント**: HTTP通信、エラーハンドリング、リトライ機能
- **Azure AD認証**: OAuth2認証フロー、トークン交換
- **トークン管理**: トークンの有効期限管理、自動更新
- **Webhook管理**: サブスクリプションのCRUD操作

### テスト方針
- **モック活用**: 外部APIのモック化
- **統合テスト**: 実際のAPIとの連携テスト
- **エラーケース**: 異常系のテスト
- **非同期テスト**: 非同期処理のテスト

## 更新履歴

- 初版作成: 2024年12月
- 更新者: 開発チーム
