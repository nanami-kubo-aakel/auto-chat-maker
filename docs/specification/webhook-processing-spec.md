# Webhook処理仕様書

## 概要

Auto Chat MakerシステムのMicrosoft Graph Webhook処理仕様を定義します。Teamsチャットの新着メッセージをリアルタイムで受信し、AI処理を経て返信案を生成します。

## Webhook概要

### 役割
- Microsoft Graph APIのChange Notifications受信
- Teamsチャットの新着メッセージ検知
- リアルタイム通知処理

### 通信プロトコル
- **プロトコル**: HTTPS必須
- **認証**: 検証トークン
- **データ形式**: JSON

## Microsoft Graph Webhook

### Change Notifications
Microsoft Graph APIのChange Notificationsを使用して、Teamsチャットの変更を監視します。

### サブスクリプション作成
```python
async def create_subscription(self, resource: str, change_type: str = "created") -> dict:
    """Webhookサブスクリプションを作成"""
    data = {
        "changeType": change_type,
        "notificationUrl": self.webhook_url,
        "resource": resource,
        "expirationDateTime": self.get_expiration_time(),
        "clientState": self.generate_client_state()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://graph.microsoft.com/v1.0/subscriptions",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=data
        )
        return response.json()
```

### サブスクリプション更新
```python
async def renew_subscription(self, subscription_id: str) -> dict:
    """サブスクリプションを更新"""
    data = {
        "expirationDateTime": self.get_expiration_time()
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=data
        )
        return response.json()
```

## Webhook受信処理

### 受信エンドポイント
```python
@app.post("/api/webhook/microsoft-graph")
async def receive_webhook(request: Request):
    """Microsoft Graph Webhook受信エンドポイント"""
    # 検証トークン処理
    if request.query_params.get("validationToken"):
        return handle_validation_token(request.query_params["validationToken"])

    # 通知データ処理
    notification_data = await request.json()
    return await process_notification(notification_data)
```

### 検証トークン処理
```python
def handle_validation_token(validation_token: str) -> Response:
    """Webhook検証トークンの処理"""
    return Response(
        content=validation_token,
        media_type="text/plain",
        status_code=200
    )
```

### 通知データ処理
```python
async def process_notification(notification_data: dict) -> dict:
    """通知データの処理"""
    try:
        # 通知データの検証
        if not validate_notification(notification_data):
            raise ValueError("Invalid notification data")

        # メッセージ処理の起動
        for value in notification_data.get("value", []):
            await process_message_change(value)

        return {"status": "success"}

    except Exception as e:
        logger.error("通知処理エラー", extra={"error": str(e)})
        return {"status": "error", "message": str(e)}
```

## メッセージ変更処理

### メッセージ変更の検出
```python
async def process_message_change(change_data: dict):
    """メッセージ変更の処理"""
    resource = change_data.get("resource")
    change_type = change_data.get("changeType")

    if not resource or not change_type:
        logger.warning("無効な変更データ", extra={"change_data": change_data})
        return

    # 新規メッセージの場合のみ処理
    if change_type == "created":
        await handle_new_message(resource)
```

### 新規メッセージ処理
```python
async def handle_new_message(resource: str):
    """新規メッセージの処理"""
    try:
        # MCP経由でメッセージ詳細取得
        message_data = await mcp_client.get_message(resource)

        # メッセージの保存
        chat_message = await save_chat_message(message_data)

        # AI処理の起動
        await trigger_ai_processing(chat_message)

        logger.info("新規メッセージ処理完了", extra={
            "message_id": message_data["message_id"],
            "sender": message_data["sender"]
        })

    except Exception as e:
        logger.error("新規メッセージ処理エラー", extra={
            "resource": resource,
            "error": str(e)
        })
```

## サブスクリプション管理

### サブスクリプション情報の保存
```python
async def save_subscription(subscription_data: dict) -> Subscription:
    """サブスクリプション情報を保存"""
    subscription = Subscription(
        subscription_id=subscription_data["id"],
        resource=subscription_data["resource"],
        resource_type="teams_chat",
        expires_at=parse_datetime(subscription_data["expirationDateTime"]),
        webhook_url=subscription_data["notificationUrl"],
        change_type=subscription_data["changeType"],
        is_active=True
    )

    return await subscription_repository.save(subscription)
```

### 定期更新処理
```python
async def renew_expired_subscriptions():
    """期限切れサブスクリプションの更新"""
    expired_subscriptions = await subscription_repository.find_expired()

    for subscription in expired_subscriptions:
        try:
            # サブスクリプション更新
            updated_data = await graph_client.renew_subscription(
                subscription.subscription_id
            )

            # 更新情報の保存
            subscription.expires_at = parse_datetime(updated_data["expirationDateTime"])
            await subscription_repository.save(subscription)

            logger.info("サブスクリプション更新完了", extra={
                "subscription_id": subscription.subscription_id
            })

        except Exception as e:
            logger.error("サブスクリプション更新エラー", extra={
                "subscription_id": subscription.subscription_id,
                "error": str(e)
            })
```

## エラーハンドリング

### Webhookエラー
| エラー種別 | 説明 | 対応 |
|-----------|------|------|
| 検証失敗 | 検証トークンが無効 | 再検証 |
| 通知データ無効 | 通知データの形式が不正 | ログ出力 |
| 処理エラー | メッセージ処理でエラー | リトライ処理 |
| サブスクリプション期限切れ | サブスクリプションが期限切れ | 自動更新 |

### リトライ処理
```python
class WebhookRetryHandler:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 5.0

    async def retry_processing(self, func, *args, **kwargs):
        """処理のリトライ"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e

                logger.warning("処理リトライ", extra={
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                await asyncio.sleep(self.retry_delay)
```

## セキュリティ要件

### Webhook URL保護
- **HTTPS必須**: 暗号化通信の使用
- **検証トークン**: リクエストの正当性確認
- **クライアント状態**: リクエストの追跡

### データ検証
```python
def validate_notification(notification_data: dict) -> bool:
    """通知データの検証"""
    required_fields = ["value", "validationToken"]

    # 必須フィールドの確認
    for field in required_fields:
        if field not in notification_data:
            return False

    # 値の形式確認
    if not isinstance(notification_data["value"], list):
        return False

    return True
```

## パフォーマンス要件

### 処理時間
- **Webhook受信**: 1秒以内
- **メッセージ取得**: 3秒以内
- **AI処理起動**: 5秒以内

### スループット
- **同時通知処理**: 10件/分
- **1日あたりの処理件数**: 1000件程度

## ログ出力

### Webhook受信ログ
```python
logger.info("Webhook受信", extra={
    "validation_token": bool(request.query_params.get("validationToken")),
    "notification_count": len(notification_data.get("value", [])),
    "timestamp": datetime.now().isoformat()
})
```

### 処理ログ
```python
logger.info("メッセージ処理開始", extra={
    "message_id": message_data["message_id"],
    "sender": message_data["sender"],
    "change_type": change_type
})
```

## テスト仕様

### 単体テスト
- Webhook受信処理のテスト
- 検証トークン処理のテスト
- 通知データ検証のテスト

### 統合テスト
- Microsoft Graph Webhookとの通信テスト
- エンドツーエンドテスト
- エラーハンドリングのテスト

### モックWebhook
```python
class MockWebhookServer:
    def __init__(self):
        self.notifications = []

    def send_notification(self, notification_data: dict):
        """モック通知送信"""
        self.notifications.append(notification_data)

    def send_validation_token(self, token: str):
        """モック検証トークン送信"""
        pass
```

## 設定管理

### 環境変数設定
```env
# Webhook Settings
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_SUBSCRIPTION_DURATION=3600
WEBHOOK_URL=https://your-app.ngrok.io/api/webhook/microsoft-graph
WEBHOOK_CHANGE_TYPE=created
```

### 設定クラス
```python
class WebhookSettings(BaseSettings):
    webhook_secret: str
    subscription_duration: int = 3600
    webhook_url: str
    change_type: str = "created"

    class Config:
        env_file = ".env"
```

## 更新履歴

- 初版作成: 2024年12月
- Webhook処理仕様: 2024年12月 - 基本仕様の定義
- 最終更新: 2024年12月
- 更新者: 開発チーム
