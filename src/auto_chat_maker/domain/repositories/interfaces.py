"""
リポジトリインターフェース定義
"""
from typing import List, Optional, Protocol

from auto_chat_maker.domain.models.chat_message import ChatMessage
from auto_chat_maker.domain.models.reply_suggestion import ReplySuggestion
from auto_chat_maker.domain.models.subscription import Subscription
from auto_chat_maker.domain.models.user import User


class UserRepository(Protocol):
    """ユーザーリポジトリインターフェース"""

    async def create(self, user: User) -> User:
        """ユーザーを作成"""
        ...

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """IDでユーザーを取得"""
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        ...

    async def get_by_microsoft_id(self, microsoft_id: str) -> Optional[User]:
        """Microsoft IDでユーザーを取得"""
        ...

    async def update(self, user: User) -> User:
        """ユーザーを更新"""
        ...

    async def delete(self, user_id: int) -> bool:
        """ユーザーを削除"""
        ...

    async def list_all(self) -> List[User]:
        """全ユーザーを取得"""
        ...


class ChatMessageRepository(Protocol):
    """チャットメッセージリポジトリインターフェース"""

    async def create(self, message: ChatMessage) -> ChatMessage:
        """メッセージを作成"""
        ...

    async def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """IDでメッセージを取得"""
        ...

    async def get_by_message_id(
        self, message_id: str
    ) -> Optional[ChatMessage]:
        """Microsoft TeamsのメッセージIDでメッセージを取得"""
        ...

    async def update(self, message: ChatMessage) -> ChatMessage:
        """メッセージを更新"""
        ...

    async def delete(self, message_id: int) -> bool:
        """メッセージを削除"""
        ...

    async def list_unprocessed(self) -> List[ChatMessage]:
        """未処理のメッセージを取得"""
        ...

    async def list_by_chat_id(self, chat_id: str) -> List[ChatMessage]:
        """チャットIDでメッセージを取得"""
        ...


class ReplySuggestionRepository(Protocol):
    """返信案リポジトリインターフェース"""

    async def create(self, suggestion: ReplySuggestion) -> ReplySuggestion:
        """返信案を作成"""
        ...

    async def get_by_id(self, suggestion_id: int) -> Optional[ReplySuggestion]:
        """IDで返信案を取得"""
        ...

    async def get_by_message_id(
        self, message_id: str
    ) -> List[ReplySuggestion]:
        """メッセージIDで返信案を取得"""
        ...

    async def update(self, suggestion: ReplySuggestion) -> ReplySuggestion:
        """返信案を更新"""
        ...

    async def delete(self, suggestion_id: int) -> bool:
        """返信案を削除"""
        ...

    async def list_selected(self) -> List[ReplySuggestion]:
        """選択済みの返信案を取得"""
        ...

    async def list_sent(self) -> List[ReplySuggestion]:
        """送信済みの返信案を取得"""
        ...


class SubscriptionRepository(Protocol):
    """サブスクリプションリポジトリインターフェース"""

    async def create(self, subscription: Subscription) -> Subscription:
        """サブスクリプションを作成"""
        ...

    async def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """IDでサブスクリプションを取得"""
        ...

    async def get_by_subscription_id(
        self, subscription_id: str
    ) -> Optional[Subscription]:
        """Microsoft GraphのサブスクリプションIDで取得"""
        ...

    async def update(self, subscription: Subscription) -> Subscription:
        """サブスクリプションを更新"""
        ...

    async def delete(self, subscription_id: int) -> bool:
        """サブスクリプションを削除"""
        ...

    async def list_active(self) -> List[Subscription]:
        """アクティブなサブスクリプションを取得"""
        ...

    async def list_expired(self) -> List[Subscription]:
        """期限切れのサブスクリプションを取得"""
        ...
