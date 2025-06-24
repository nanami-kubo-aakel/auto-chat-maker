# Phase 1: 基盤構築 - 詳細クラス設計書

## 概要

Auto Chat MakerシステムのPhase 1（基盤構築）における詳細なクラス設計を定義します。クリーンアーキテクチャの原則に従い、各クラスの役割、責任、依存関係を明確にします。

## 設計方針

### クリーンアーキテクチャ原則
- **依存関係の方向**: 内側（ドメイン）に向かう
- **単一責任原則**: 各クラスは1つの責任を持つ
- **依存性注入**: 外部依存はインターフェースを通じて注入
- **テスタビリティ**: 各クラスが独立してテスト可能

### 実装順序
1. **設定管理層** - 全機能の前提条件
2. **ユーティリティ層** - 共通機能の提供
3. **ドメイン層基盤** - ビジネスロジックの基盤
4. **FastAPI基盤** - アプリケーションの起動基盤

## 1. 設定管理層 (config/)

### 1.1 基本設定クラス

#### `config/settings.py`
```python
class Settings(BaseSettings):
    """アプリケーション基本設定クラス"""

    # アプリケーション基本設定
    app_name: str = "Auto Chat Maker"
    app_version: str = "1.0.0"
    debug: bool = False

    # データベース設定
    database_url: str = "sqlite:///./auto_chat_maker.db"

    # ログ設定
    log_level: str = "INFO"
    log_format: str = "json"

    # セキュリティ設定
    secret_key: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
```

**責任**:
- 環境変数からの設定読み込み
- 設定値のバリデーション
- デフォルト値の提供

**依存関係**:
- `pydantic.BaseSettings` - 設定管理基盤

#### `config/mcp_settings.py`
```python
class MCPSettings(BaseSettings):
    """MCPサーバー設定クラス"""

    # MCPサーバー設定
    mcp_server_url: str
    mcp_api_key: str
    mcp_timeout: int = 30

    # 接続設定
    mcp_max_retries: int = 3
    mcp_retry_delay: int = 1

    class Config:
        env_prefix = "MCP_"
```

**責任**:
- MCPサーバー接続設定の管理
- 接続パラメータのバリデーション

**依存関係**:
- `pydantic.BaseSettings` - 設定管理基盤

#### `config/azure_settings.py`
```python
class AzureSettings(BaseSettings):
    """Azure AD設定クラス"""

    # Azure AD設定
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str

    # Graph API設定
    graph_api_url: str = "https://graph.microsoft.com/v1.0"
    graph_api_scopes: List[str] = ["https://graph.microsoft.com/.default"]

    class Config:
        env_prefix = "AZURE_"
```

**責任**:
- Azure AD認証設定の管理
- Graph API接続設定の管理

**依存関係**:
- `pydantic.BaseSettings` - 設定管理基盤

#### `config/__init__.py`
```python
class ConfigManager:
    """設定管理クラス"""

    def __init__(self):
        self.settings = Settings()
        self.mcp_settings = MCPSettings()
        self.azure_settings = AzureSettings()

    def get_settings(self) -> Settings:
        """基本設定を取得"""
        return self.settings

    def get_mcp_settings(self) -> MCPSettings:
        """MCP設定を取得"""
        return self.mcp_settings

    def get_azure_settings(self) -> AzureSettings:
        """Azure設定を取得"""
        return self.azure_settings
```

**責任**:
- 全設定クラスの統合管理
- 設定の一元化アクセス

**依存関係**:
- `Settings` - 基本設定
- `MCPSettings` - MCP設定
- `AzureSettings` - Azure設定

## 2. ユーティリティ層 (utils/)

### 2.1 ログ設定

#### `utils/logger.py`
```python
class LoggerConfig:
    """ログ設定クラス"""

    def __init__(self, log_level: str, log_format: str):
        self.log_level = log_level
        self.log_format = log_format

    def setup_logging(self) -> None:
        """ログ設定を初期化"""
        pass

class AppLogger:
    """アプリケーションログクラス"""

    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)

    def info(self, message: str, **kwargs) -> None:
        """情報ログを出力"""
        pass

    def error(self, message: str, **kwargs) -> None:
        """エラーログを出力"""
        pass

    def debug(self, message: str, **kwargs) -> None:
        """デバッグログを出力"""
        pass
```

**責任**:
- 構造化ログの設定
- ログ出力の統一化
- ログレベルの管理

**依存関係**:
- `structlog` - 構造化ログライブラリ

### 2.2 カスタム例外

#### `utils/exceptions.py`
```python
class AutoChatMakerException(Exception):
    """Auto Chat Maker基本例外クラス"""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ConfigurationError(AutoChatMakerException):
    """設定エラー例外"""
    pass

class MCPConnectionError(AutoChatMakerException):
    """MCP接続エラー例外"""
    pass

class AuthenticationError(AutoChatMakerException):
    """認証エラー例外"""
    pass

class ValidationError(AutoChatMakerException):
    """バリデーションエラー例外"""
    pass
```

**責任**:
- アプリケーション固有の例外定義
- エラーハンドリングの統一化

**依存関係**:
- なし（基本例外クラス）

## 3. ドメイン層基盤 (domain/)

### 3.1 エンティティ基盤

#### `domain/models/base.py`
```python
class BaseEntity:
    """エンティティ基本クラス"""

    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update(self) -> None:
        """更新日時を更新"""
        self.updated_at = datetime.utcnow()

    def __eq__(self, other) -> bool:
        """等価性チェック"""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """ハッシュ値生成"""
        return hash(self.id)
```

**責任**:
- エンティティの共通機能提供
- ID管理とタイムスタンプ管理
- 等価性とハッシュ値の実装

**依存関係**:
- `uuid` - ID生成
- `datetime` - タイムスタンプ管理

#### `domain/models/user.py`
```python
class User(BaseEntity):
    """ユーザーエンティティ"""

    def __init__(self, email: str, name: str, id: Optional[str] = None):
        super().__init__(id)
        self.email = email
        self.name = name

    @property
    def display_name(self) -> str:
        """表示名を取得"""
        return self.name or self.email

    def is_valid(self) -> bool:
        """ユーザー情報の妥当性チェック"""
        return bool(self.email and self.name)
```

**責任**:
- ユーザー情報の管理
- ユーザー情報の妥当性チェック

**依存関係**:
- `BaseEntity` - エンティティ基本クラス

#### `domain/models/chat_message.py`
```python
class ChatMessage(BaseEntity):
    """チャットメッセージエンティティ"""

    def __init__(
        self,
        user_id: str,
        message_id: str,
        content: str,
        sender: str,
        thread_id: str,
        message_type: str = "text",
        channel_id: Optional[str] = None,
        team_id: Optional[str] = None,
        sent_at: Optional[datetime] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.user_id = user_id
        self.message_id = message_id
        self.content = content
        self.sender = sender
        self.thread_id = thread_id
        self.message_type = message_type
        self.channel_id = channel_id
        self.team_id = team_id
        self.sent_at = sent_at or datetime.utcnow()
        self.processed_at: Optional[datetime] = None

    def mark_as_processed(self) -> None:
        """処理済みとしてマーク"""
        self.processed_at = datetime.utcnow()
        self.update()

    def is_processed(self) -> bool:
        """処理済みかどうかチェック"""
        return self.processed_at is not None

    def is_text_message(self) -> bool:
        """テキストメッセージかどうかチェック"""
        return self.message_type == "text"
```

**責任**:
- チャットメッセージ情報の管理
- メッセージの処理状態管理
- メッセージタイプの判定

**依存関係**:
- `BaseEntity` - エンティティ基本クラス

#### `domain/models/reply_suggestion.py`
```python
class ReplySuggestion(BaseEntity):
    """返信案エンティティ"""

    def __init__(
        self,
        chat_message_id: str,
        content: str,
        confidence_score: Optional[float] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.chat_message_id = chat_message_id
        self.content = content
        self.confidence_score = confidence_score or 0.0
        self.selected = False

    def select(self) -> None:
        """返信案を選択"""
        self.selected = True
        self.update()

    def deselect(self) -> None:
        """返信案の選択を解除"""
        self.selected = False
        self.update()

    def is_high_confidence(self) -> bool:
        """高信頼度かどうかチェック"""
        return self.confidence_score >= 0.8

    def is_selected(self) -> bool:
        """選択済みかどうかチェック"""
        return self.selected
```

**責任**:
- 返信案情報の管理
- 返信案の選択状態管理
- 信頼度スコアの管理

**依存関係**:
- `BaseEntity` - エンティティ基本クラス

### 3.2 リポジトリインターフェース

#### `domain/repositories/interfaces.py`
```python
class UserRepository(ABC):
    """ユーザーリポジトリインターフェース"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """ユーザーを保存"""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """IDでユーザーを検索"""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを検索"""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """ユーザーを削除"""
        pass

class ChatMessageRepository(ABC):
    """チャットメッセージリポジトリインターフェース"""

    @abstractmethod
    async def save(self, message: ChatMessage) -> ChatMessage:
        """メッセージを保存"""
        pass

    @abstractmethod
    async def find_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """IDでメッセージを検索"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[ChatMessage]:
        """ユーザーIDでメッセージを検索"""
        pass

    @abstractmethod
    async def find_unprocessed(self) -> List[ChatMessage]:
        """未処理メッセージを検索"""
        pass

    @abstractmethod
    async def delete(self, message_id: str) -> bool:
        """メッセージを削除"""
        pass

class ReplySuggestionRepository(ABC):
    """返信案リポジトリインターフェース"""

    @abstractmethod
    async def save(self, suggestion: ReplySuggestion) -> ReplySuggestion:
        """返信案を保存"""
        pass

    @abstractmethod
    async def find_by_chat_message_id(self, chat_message_id: str) -> List[ReplySuggestion]:
        """チャットメッセージIDで返信案を検索"""
        pass

    @abstractmethod
    async def find_selected(self, chat_message_id: str) -> Optional[ReplySuggestion]:
        """選択済み返信案を検索"""
        pass

    @abstractmethod
    async def delete(self, suggestion_id: str) -> bool:
        """返信案を削除"""
        pass
```

**責任**:
- データアクセスの抽象化
- ドメイン層とインフラ層の分離
- テスタビリティの確保

**依存関係**:
- `ABC` - 抽象基底クラス
- ドメインエンティティ

## 4. FastAPI基盤 (main.py)

### 4.1 アプリケーション基盤

#### `main.py`
```python
class AutoChatMakerApp:
    """Auto Chat Makerアプリケーションクラス"""

    def __init__(self):
        self.app = FastAPI(
            title="Auto Chat Maker",
            description="AI-powered Teams chat assistant",
            version="1.0.0"
        )
        self.config_manager = ConfigManager()
        self.logger = AppLogger(__name__)
        self._setup_middleware()
        self._setup_routes()
        self._setup_exception_handlers()

    def _setup_middleware(self) -> None:
        """ミドルウェアを設定"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self) -> None:
        """ルートを設定"""
        # ヘルスチェック
        self.app.get("/health")(self._health_check)

        # APIルート（後で実装）
        # self.app.include_router(auth_router, prefix="/api/auth")
        # self.app.include_router(webhook_router, prefix="/api/webhook")

    def _setup_exception_handlers(self) -> None:
        """例外ハンドラーを設定"""
        self.app.add_exception_handler(
            AutoChatMakerException,
            self._handle_auto_chat_maker_exception
        )
        self.app.add_exception_handler(
            Exception,
            self._handle_generic_exception
        )

    async def _health_check(self) -> Dict[str, str]:
        """ヘルスチェックエンドポイント"""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    async def _handle_auto_chat_maker_exception(
        self, request: Request, exc: AutoChatMakerException
    ) -> JSONResponse:
        """Auto Chat Maker例外ハンドラー"""
        self.logger.error(f"Application error: {exc.message}", error_code=exc.error_code)
        return JSONResponse(
            status_code=400,
            content={"error": exc.message, "error_code": exc.error_code}
        )

    async def _handle_generic_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """汎用例外ハンドラー"""
        self.logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

    def get_app(self) -> FastAPI:
        """FastAPIアプリケーションを取得"""
        return self.app

# アプリケーションインスタンス
app_instance = AutoChatMakerApp()
app = app_instance.get_app()
```

**責任**:
- FastAPIアプリケーションの初期化
- ミドルウェアの設定
- ルートの設定
- 例外ハンドリングの設定

**依存関係**:
- `FastAPI` - Webフレームワーク
- `ConfigManager` - 設定管理
- `AppLogger` - ログ出力
- `AutoChatMakerException` - カスタム例外

## 5. 実装順序と依存関係

### 実装順序
1. **utils/exceptions.py** - カスタム例外（依存なし）
2. **utils/logger.py** - ログ設定（例外に依存）
3. **config/settings.py** - 基本設定（ログに依存）
4. **config/mcp_settings.py** - MCP設定（基本設定に依存）
5. **config/azure_settings.py** - Azure設定（基本設定に依存）
6. **config/__init__.py** - 設定管理（全設定に依存）
7. **domain/models/base.py** - エンティティ基盤（依存なし）
8. **domain/models/user.py** - ユーザーエンティティ（基盤に依存）
9. **domain/models/chat_message.py** - メッセージエンティティ（基盤に依存）
10. **domain/models/reply_suggestion.py** - 返信案エンティティ（基盤に依存）
11. **domain/repositories/interfaces.py** - リポジトリインターフェース（エンティティに依存）
12. **main.py** - アプリケーション基盤（全基盤に依存）

### 依存関係図
```
utils/exceptions.py
    ↓
utils/logger.py
    ↓
config/settings.py
    ↓
config/mcp_settings.py
config/azure_settings.py
    ↓
config/__init__.py
    ↓
domain/models/base.py
    ↓
domain/models/user.py
domain/models/chat_message.py
domain/models/reply_suggestion.py
    ↓
domain/repositories/interfaces.py
    ↓
main.py
```

## 6. テスト戦略

### 単体テスト対象
- **設定クラス**: 設定値のバリデーションテスト
- **エンティティ**: ビジネスルールのテスト
- **リポジトリインターフェース**: モックによるテスト
- **アプリケーション基盤**: 起動・設定テスト

### テスト方針
- **AAAパターン**: Arrange, Act, Assert
- **依存性注入**: テスト可能な設計
- **モック活用**: 外部依存のモック化

## 更新履歴

- 初版作成: 2024年12月
- 更新者: 開発チーム
