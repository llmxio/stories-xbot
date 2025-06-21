"""Bot middlewares for the Telegram bot."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_logger
from db.redis import UserCache
from db.schemas import UserCreate
from services import UserService

log = get_logger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    Middleware for handling user-related operations.

    This middleware:
    1. Blocks bot users
    2. Checks if user is blocked
    3. Checks if user is temporarily suspended
    4. Saves user information
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)
        log.debug("Initialized UserMiddleware with session %s", session)

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
        log.debug("Processing message from user %d in chat %d", user_id, chat_id)

        # Block bot users
        if event.from_user.is_bot:
            if event.from_user.id != data["bot"].id:
                log.info("Blocking bot user %d", user_id)
                self.user_service.block_user(chat_id, True)
            return

        # Try to get user from cache first
        cached_user = await UserCache.get_from_cache(chat_id)

        # If not in cache, try database
        if not cached_user:
            existing_user = await self.user_service.get_user_by_chat_id(chat_id)
            if existing_user:
                # Convert User to UserCache for consistency
                cached_user = UserCache.model_validate(existing_user.model_dump())

        # Check if user is blocked (using cached data if available)
        if cached_user and cached_user.is_blocked:
            log.info("Blocked user %d attempted to use the bot", user_id)
            return

        # Check if user is temporarily suspended (only for non-bot users)
        if event.from_user.id != data["bot"].id:
            is_suspended = await self.user_service.is_user_temporarily_suspended(chat_id)
            if is_suspended:
                remaining = await self.user_service.get_suspension_remaining(chat_id)
                minutes = (remaining + 59) // 60  # Round up to nearest minute
                log.info(
                    "Suspended user %d attempted to use the bot, %d minutes remaining",
                    user_id,
                    minutes,
                )
                try:
                    await event.answer(
                        f"🚫 You are temporarily suspended for {minutes} minute{'s' if minutes != 1 else ''}."
                    )
                except Exception as e:
                    log.exception("Failed to answer suspended user %d: %s", user_id, e)
                return

        # Determine if we need to save user information
        should_save = False
        if not cached_user:
            should_save = True
        else:
            # Check if any user attributes have changed
            current_premium = event.from_user.is_premium or False
            current_username = event.from_user.username or ""
            current_last_name = event.from_user.last_name or ""
            current_language_code = event.from_user.language_code or ""
            current_added_to_attachment_menu = event.from_user.added_to_attachment_menu or False
            current_can_join_groups = event.from_user.can_join_groups or True
            current_can_read_all_group_messages = event.from_user.can_read_all_group_messages or False
            current_supports_inline_queries = event.from_user.supports_inline_queries or False
            current_can_connect_to_business = event.from_user.can_connect_to_business or False

            if (
                cached_user.is_premium != current_premium
                or cached_user.username != current_username
                or cached_user.first_name != event.from_user.first_name
                or cached_user.last_name != current_last_name
                or cached_user.language_code != current_language_code
                or cached_user.added_to_attachment_menu != current_added_to_attachment_menu
                or cached_user.can_join_groups != current_can_join_groups
                or cached_user.can_read_all_group_messages != current_can_read_all_group_messages
                or cached_user.supports_inline_queries != current_supports_inline_queries
                or cached_user.can_connect_to_business != current_can_connect_to_business
            ):
                should_save = True

        # Save user information if needed
        if should_save:
            try:
                log.debug("Saving user information for user %d", user_id)
                user = await self.user_service.save_user(
                    UserCreate(
                        chat_id=chat_id,
                        username=event.from_user.username or "",
                        first_name=event.from_user.first_name,
                        last_name=event.from_user.last_name,
                        language_code=event.from_user.language_code,
                        is_bot=event.from_user.is_bot,
                        is_premium=event.from_user.is_premium or False,
                        added_to_attachment_menu=event.from_user.added_to_attachment_menu or False,
                        can_join_groups=event.from_user.can_join_groups or True,
                        can_read_all_group_messages=event.from_user.can_read_all_group_messages or False,
                        supports_inline_queries=event.from_user.supports_inline_queries or False,
                        can_connect_to_business=event.from_user.can_connect_to_business or False,
                    )
                )
                # Update cache with new user data
                cached_user = UserCache.model_validate(user.model_dump())
            except Exception as e:
                log.exception("Failed to save user %d: %s", user_id, e)
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

    def __init__(self, session: AsyncSession):
        self.session = session
        log.debug("Initialized LoggingMiddleware with session %s", session)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            text = event.text if hasattr(event, "text") else ""
            user_id = event.from_user.id if event.from_user else None
            log.debug(
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

    def __init__(self, session: AsyncSession):
        self.session = session
        log.debug("Initialized LongOperationMiddleware with session %s", session)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # If no flag exists on handler
        if not long_operation_type:
            return await handler(event, data)

        # If flag exists, send chat action
        if not isinstance(event, Message):
            return await handler(event, data)

        log.debug(
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
                log.debug(
                    "Completed long operation '%s' for chat %d",
                    long_operation_type,
                    event.chat.id,
                )
                return result
        except Exception as e:
            log.exception(
                "Error during long operation '%s' for chat %d: %s",
                long_operation_type,
                event.chat.id,
                e,
            )
            raise
