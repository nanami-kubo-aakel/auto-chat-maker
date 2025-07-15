"""
返信案エンティティ
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReplySuggestion(BaseModel):
    """返信案エンティティ"""

    id: Optional[int] = None
    message_id: str = Field(..., description="関連するメッセージID")
    content: str = Field(..., description="返信案の内容")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="信頼度スコア")
    is_selected: bool = Field(False, description="選択済みフラグ")
    is_sent: bool = Field(False, description="送信済みフラグ")
    sent_at: Optional[datetime] = Field(None, description="送信日時")
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
            f"ReplySuggestion(id={self.id}, message_id={self.message_id}, "
            f"confidence={self.confidence_score})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def select(self) -> None:
        """返信案を選択"""
        self.is_selected = True
        self.updated_at = datetime.utcnow()

    def mark_as_sent(self) -> None:
        """返信案を送信済みとしてマーク"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
