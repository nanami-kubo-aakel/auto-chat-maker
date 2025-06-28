"""
ユーザーエンティティ
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """ユーザーエンティティ"""

    id: Optional[int] = None
    email: str = Field(..., description="ユーザーのメールアドレス")
    name: str = Field(..., description="ユーザーの表示名")
    microsoft_id: Optional[str] = Field(
        None, description="Microsoft 365のユーザーID"
    )
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
        return f"User(id={self.id}, email={self.email}, name={self.name})"

    def __repr__(self) -> str:
        return self.__str__()
