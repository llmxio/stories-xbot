"""Bot middlewares for the Telegram bot."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.orm import Session

from config.logger import get_logger
from db.repository import (
    block_user,
    get_suspension_remaining,
    is_user_blocked,
    is_user_temporarily_suspended,
    save_user,
)

logger = get_logger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    Middleware for handling user-related operations.

    This middleware:
    1. Blocks bot users
    2. Checks if user is blocked
    3. Checks if user is temporarily suspended
    4. Saves user information
    """

    def __init__(self, session: Session):
        self.session = session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        # Block bot users
        if event.from_user.is_bot:
            if event.from_user.id != data["bot"].id:
                await block_user(self.session, str(event.from_user.id), True)
            return

        # Check if user is blocked
        if is_user_blocked(self.session, str(event.from_user.id)):
            return

        # Check if user is temporarily suspended
        if event.from_user.id != data["bot"].id and is_user_temporarily_suspended(
            self.session, str(event.from_user.id)
        ):
            remaining = get_suspension_remaining(self.session, str(event.from_user.id))
            minutes = (remaining + 59) // 60  # Round up to nearest minute
            try:
                await event.answer(
                    f"🚫 You are temporarily suspended for {minutes} minute{'s' if minutes != 1 else ''}."
                )
            except Exception as e:
                logger.exception("Failed to answer: %s", e)
            return

        # Save user information
        try:
            await save_user(self.session, event.from_user)
        except Exception as e:
            logger.exception("Failed to save user: %s", e)

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging updates and messages.

    This middleware logs:
    1. User ID
    2. Update type
    3. Message text (if available)
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            text = event.text if hasattr(event, "text") else ""
            logger.debug(
                "Update from %s",
                event.from_user.id if event.from_user else "unknown",
                extra={
                    "userId": event.from_user.id if event.from_user else None,
                    "updateType": event.content_type,
                    "text": text,
                },
            )
        return await handler(event, data)


class LongOperation(BaseMiddleware):
    """
    Middleware for handling long operations in a Telegram bot.

    This middleware checks for a 'long_operation' flag in the handler data and sends
    appropriate chat action (like 'typing', 'upload_photo', etc.) to the user while
    the handler is processing.

    The middleware will automatically send the specified chat action during handler execution.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # If no flag exists on handler
        if not long_operation_type:
            return await handler(event, data)

        # If flag exists, send chat action
        async with ChatActionSender(
            action=long_operation_type,
            chat_id=event.chat.id,
            bot=data["bot"],
        ):
            return await handler(event, data)
