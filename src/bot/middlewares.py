"""Bot middlewares for the Telegram bot."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession as Session

from config import get_config, get_logger
from db.redis import CachedUser
from db.repository import UserRepository
from db.schemas import User as UserCreate

LOG_LEVEL = get_config().LOG_LEVEL

logger = get_logger(__name__, log_level=LOG_LEVEL)


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
        self.user_repo = UserRepository(session)
        logger.debug("Initialized UserMiddleware with session")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        chat_id = event.chat.id
        user_id = event.from_user.id
        logger.debug("Processing message from user %d in chat %d", user_id, chat_id)

        # Block bot users
        if event.from_user.is_bot:
            if event.from_user.id != data["bot"].id:
                logger.info("Blocking bot user %d", user_id)
                self.user_repo.block_user(chat_id, True)
            return

        # Try to get user from cache first
        cached_user = CachedUser.get_from_cache(chat_id)

        # If not in cache, try database
        if not cached_user:
            existing_user = self.user_repo.get_user_by_chat_id(chat_id)
            if existing_user:
                cached_user = CachedUser.get_from_cache(existing_user.id)

        # Check if user is blocked (using cached data if available)
        if cached_user and cached_user.is_blocked or (not cached_user and self.user_repo.is_user_blocked(chat_id)):
            logger.info("Blocked user %d attempted to use the bot", user_id)
            return

        # Check if user is temporarily suspended (using cached data if available)
        is_suspended = False
        if event.from_user.id != data["bot"].id:
            if cached_user and cached_user.is_suspended:
                is_suspended = True
                remaining = cached_user.suspension_remaining
            else:
                is_suspended = self.user_repo.is_user_temporarily_suspended(chat_id)
                remaining = self.user_repo.get_suspension_remaining(chat_id) if is_suspended else 0

            if is_suspended:
                minutes = (remaining + 59) // 60  # Round up to nearest minute
                logger.info(
                    "Suspended user %d attempted to use the bot, %d minutes remaining",
                    user_id,
                    minutes,
                )
                try:
                    await event.answer(
                        f"🚫 You are temporarily suspended for {minutes} minute{'s' if minutes != 1 else ''}."
                    )
                except Exception as e:
                    logger.exception("Failed to answer suspended user %d: %s", user_id, e)
                return

        # Only save user information if it has changed or user doesn't exist
        should_save = False
        if not cached_user:
            should_save = True
        else:
            # Check if any user attributes have changed
            if cached_user.is_premium != (event.from_user.is_premium or False) or cached_user.username != (
                event.from_user.username or ""
            ):
                should_save = True

        if should_save:
            try:
                logger.debug("Saving user information for user %d", user_id)
                user = self.user_repo.save_user(
                    UserCreate(
                        is_bot=event.from_user.is_bot,
                        is_premium=event.from_user.is_premium or False,
                        chat_id=chat_id,
                        username=event.from_user.username or "",
                    )
                )
                # Update cache with new user data
                cached_user = user
            except Exception as e:
                logger.exception("Failed to save user %d: %s", user_id, e)
                # If save fails but we have cached user, continue with that
                if not cached_user:
                    # If we have no cached data and save failed, we can't proceed
                    return

        # Add user to handler data for easy access
        data["user"] = cached_user

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
            user_id = event.from_user.id if event.from_user else None
            logger.debug(
                "Processing update from user %s",
                user_id or "unknown",
                extra={
                    "userId": user_id,
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
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # If no flag exists on handler
        if not long_operation_type:
            return await handler(event, data)

        # If flag exists, send chat action
        logger.debug(
            "Starting long operation '%s' for chat %d",
            long_operation_type,
            event.chat.id,
        )
        try:
            async with ChatActionSender(
                action=long_operation_type,
                chat_id=event.chat.id,
                bot=data["bot"],
            ):
                result = await handler(event, data)
                logger.debug(
                    "Completed long operation '%s' for chat %d",
                    long_operation_type,
                    event.chat.id,
                )
                return result
        except Exception as e:
            logger.exception(
                "Error during long operation '%s' for chat %d: %s",
                long_operation_type,
                event.chat.id,
                e,
            )
            raise
