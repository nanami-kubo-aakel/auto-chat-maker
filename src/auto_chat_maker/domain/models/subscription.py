"""
サブスクリプションエンティティ
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Subscription(BaseModel):
    """Webhookサブスクリプションエンティティ"""

    id: Optional[int] = None
    subscription_id: str = Field(
        ..., description="Microsoft GraphのサブスクリプションID"
    )
    resource: str = Field(..., description="リソースURL")
    change_type: str = Field("created,updated", description="変更タイプ")
    client_state: Optional[str] = Field(None, description="クライアント状態")
    notification_url: str = Field(..., description="通知URL")
    expiration_date_time: datetime = Field(..., description="有効期限")
    is_active: bool = Field(True, description="アクティブ状態")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="作成日時"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新日時"
    )

    class Config:
        from_attributes = True

    def __str__(self) -> str:
        return (
            f"Subscription(id={self.id}, "
            f"subscription_id={self.subscription_id}, "
            f"resource={self.resource})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def is_expired(self) -> bool:
        """サブスクリプションが期限切れかどうかを判定"""
        return datetime.utcnow() > self.expiration_date_time

    def deactivate(self) -> None:
        """サブスクリプションを非アクティブにする"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """サブスクリプションをアクティブにする"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
