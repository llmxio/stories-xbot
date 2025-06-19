"""Bot filters for the Telegram bot."""

from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import get_config


class ChatType(BaseFilter):
    """Filter messages by chat type."""

    def __init__(self, chat_type: str | list[str]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        return message.chat.type in self.chat_type


class HasUsernames(BaseFilter):
    """Filter messages that contain usernames."""

    async def __call__(self, message: Message) -> bool | dict[str, Any]:
        # If no entities exist, return None (empty list)
        entities = message.entities or []
        message_text = message.text or ""

        # Check for usernames and extract them from text
        found_usernames = [
            item.extract_from(message_text) for item in entities if item.type == "mention"
        ]

        # If usernames found, pass them to handler
        if len(found_usernames) > 0:
            return {"usernames": found_usernames}

        # If no usernames found, return False
        return False


class IsAdmin(BaseFilter):
    """Filter messages from admin users."""

    async def __call__(self, message: Message) -> bool:
        """Check if the message is from an admin user."""
        if not message.from_user:
            return False
        return message.from_user.id == get_config().BOT_ADMIN_ID


class IsPremium(BaseFilter):
    """Filter messages from premium users."""

    async def __call__(self, message: Message) -> bool:
        """Check if the message is from a premium user."""
        if not message.from_user:
            return False
        return bool(message.from_user.is_premium)
