# Azure AD認証仕様書

## 概要

Auto Chat MakerシステムとMicrosoft Azure Active Directory（Azure AD）との認証連携仕様を定義します。OAuth2認証フローを使用してMicrosoft Graph APIへのアクセス権限を取得します。

## Azure AD概要

### 役割
- Microsoft 365サービスの認証・認可
- Microsoft Graph APIへのアクセス制御
- ユーザー情報の管理

### 認証方式
- **認証プロトコル**: OAuth2
- **認可方式**: Authorization Code Flow
- **トークン形式**: JWT（JSON Web Token）

## アプリケーション登録

### Azure Portalでの設定
1. **アプリ登録**: 新しいアプリケーションの登録
2. **APIアクセス許可**: 必要な権限の設定
3. **認証設定**: リダイレクトURIの設定
4. **証明書とシークレット**: クライアントシークレットの生成

### 必要な権限
| 権限名 | 説明 | 用途 |
|--------|------|------|
| `Chat.Read` | チャットの読み取り | チャットメッセージ取得 |
| `Chat.ReadWrite` | チャットの読み書き | チャットメッセージ送信 |
| `ChatMessage.Send` | チャットメッセージ送信 | 返信送信 |
| `ChatMessage.ReadWrite` | チャットメッセージ読み書き | メッセージ操作 |
| `User.Read.All` | ユーザー情報読み取り | ユーザー情報取得 |
| `offline_access` | オフラインアクセス | リフレッシュトークン取得 |
| `ChannelMessage.Read.All` | チャンネルメッセージ読み取り | チームチャット対応 |

## 設定管理

### 環境変数設定
```env
# Azure AD Settings
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback
AZURE_SCOPE=https://graph.microsoft.com/.default
AZURE_AUTHORITY=https://login.microsoftonline.com/your_tenant_id
```

### 設定クラス
```python
class AzureADSettings(BaseSettings):
    client_id: str
    client_secret: str
    tenant_id: str
    redirect_uri: str
    scope: str = "https://graph.microsoft.com/.default"
    authority: str

    class Config:
        env_file = ".env"

    @property
    def authority_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}"
```

## 認証フロー

### OAuth2 Authorization Code Flow
```
1. ユーザー → アプリケーション: 認証要求
2. アプリケーション → Azure AD: 認証URL生成
3. ユーザー → Azure AD: 認証実行
4. Azure AD → アプリケーション: 認証コード返却
5. アプリケーション → Azure AD: トークン要求
6. Azure AD → アプリケーション: アクセストークン・リフレッシュトークン返却
```

### 認証URL生成
```python
def generate_auth_url(self, state: str = None) -> str:
    """認証URLを生成"""
    params = {
        'client_id': self.client_id,
        'response_type': 'code',
        'redirect_uri': self.redirect_uri,
        'scope': self.scope,
        'response_mode': 'query'
    }
    if state:
        params['state'] = state

    return f"{self.authority_url}/oauth2/v2.0/authorize?{urlencode(params)}"
```

### トークン取得
```python
async def get_token_from_code(self, code: str) -> dict:
    """認証コードからトークンを取得"""
    data = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'code': code,
        'redirect_uri': self.redirect_uri,
        'grant_type': 'authorization_code'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.authority_url}/oauth2/v2.0/token",
            data=data
        )
        return response.json()
```

## トークン管理

### トークン情報
```python
@dataclass
class TokenInfo:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    scope: str
    expires_at: datetime

    @classmethod
    def from_response(cls, response: dict) -> 'TokenInfo':
        expires_at = datetime.now() + timedelta(seconds=response['expires_in'])
        return cls(
            access_token=response['access_token'],
            refresh_token=response.get('refresh_token'),
            expires_in=response['expires_in'],
            token_type=response['token_type'],
            scope=response['scope'],
            expires_at=expires_at
        )
```

### トークン管理クラス
```python
class TokenManager:
    def __init__(self):
        self._token_info: Optional[TokenInfo] = None

    def set_token(self, token_info: TokenInfo):
        """トークンを設定"""
        self._token_info = token_info

    def get_access_token(self) -> Optional[str]:
        """アクセストークンを取得"""
        if self._token_info and self.is_token_valid():
            return self._token_info.access_token
        return None

    def is_token_valid(self) -> bool:
        """トークンの有効性チェック"""
        if not self._token_info:
            return False
        return datetime.now() < self._token_info.expires_at

    async def refresh_token(self) -> bool:
        """リフレッシュトークンでトークン更新"""
        if not self._token_info or not self._token_info.refresh_token:
            return False

        # リフレッシュトークンでの更新処理
        pass
```

## 認証ミドルウェア

### FastAPI認証ミドルウェア
```python
class AzureADAuthMiddleware:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    async def __call__(self, request: Request, call_next):
        # 認証チェック処理
        if not self.token_manager.get_access_token():
            return RedirectResponse(url="/auth/login")

        response = await call_next(request)
        return response
```

### 認証デコレータ
```python
def require_auth(func):
    """認証必須デコレータ"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 認証チェック処理
        pass
    return wrapper
```

## エラーハンドリング

### 認証エラー
| エラーコード | 説明 | 対応 |
|-------------|------|------|
| `invalid_client` | クライアントID無効 | 設定確認 |
| `invalid_grant` | 認証コード無効 | 再認証 |
| `invalid_scope` | スコープ無効 | 権限確認 |
| `unauthorized_client` | クライアント認証失敗 | シークレット確認 |
| `unsupported_grant_type` | 認可方式無効 | 実装確認 |

### エラーハンドリング
```python
class AuthError(Exception):
    def __init__(self, error: str, description: str = None):
        self.error = error
        self.description = description
        super().__init__(description or error)

async def handle_auth_error(error: AuthError) -> JSONResponse:
    """認証エラーの処理"""
    if error.error == 'invalid_grant':
        return RedirectResponse(url="/auth/login")

    return JSONResponse(
        status_code=401,
        content={"error": error.error, "description": error.description}
    )
```

## セキュリティ要件

### 通信暗号化
- **プロトコル**: HTTPS必須
- **証明書**: 有効なSSL証明書
- **TLS**: 1.2以上

### トークン管理
- **保存場所**: メモリキャッシュまたは環境変数
- **有効期限**: 1時間（デフォルト）
- **自動更新**: リフレッシュトークンによる更新

### セキュリティヘッダー
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## ログ出力

### 認証ログ
```python
logger.info("認証開始", extra={
    "user_id": user_id,
    "auth_method": "oauth2",
    "timestamp": datetime.now().isoformat()
})

logger.info("トークン取得成功", extra={
    "user_id": user_id,
    "expires_in": token_info.expires_in,
    "scope": token_info.scope
})
```

### セキュリティログ
```python
logger.warning("認証失敗", extra={
    "error": error.error,
    "description": error.description,
    "ip_address": request.client.host
})
```

## テスト仕様

### 単体テスト
- 認証URL生成のテスト
- トークン取得のテスト
- トークン管理のテスト

### 統合テスト
- Azure ADとの通信テスト
- 認証フローのテスト
- エラーハンドリングのテスト

### モック認証
```python
class MockAzureAD:
    def __init__(self):
        self.users = {}
        self.tokens = {}

    def authenticate(self, username: str, password: str) -> dict:
        """モック認証"""
        pass

    def generate_token(self, user_id: str) -> dict:
        """モックトークン生成"""
        pass
```

## 更新履歴

- 初版作成: 2024年12月
- Azure AD認証仕様: 2024年12月 - 基本仕様の定義
- 最終更新: 2024年12月
- 更新者: 開発チーム
