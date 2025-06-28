"""
チャットメッセージエンティティ
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """チャットメッセージエンティティ"""

    id: Optional[int] = None
    message_id: str = Field(..., description="Microsoft TeamsのメッセージID")
    chat_id: str = Field(..., description="チャットID")
    thread_id: Optional[str] = Field(None, description="スレッドID")
    content: str = Field(..., description="メッセージ内容")
    sender_id: str = Field(..., description="送信者ID")
    sender_name: str = Field(..., description="送信者名")
    message_type: str = Field("text", description="メッセージタイプ")
    sent_at: datetime = Field(..., description="送信日時")
    processed_at: Optional[datetime] = Field(None, description="処理日時")
    is_processed: bool = Field(False, description="処理済みフラグ")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="作成日時"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新日時"
    )

    class Config:
        from_attributes = True

    def __str__(self) -> str:
        return f"ChatMessage(id={self.id}, message_id={self.message_id}, sender={self.sender_name})"

    def __repr__(self) -> str:
        return self.__str__()

    def mark_as_processed(self) -> None:
        """メッセージを処理済みとしてマーク"""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
