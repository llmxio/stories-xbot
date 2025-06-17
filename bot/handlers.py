"""Bot handlers for the Telegram bot."""

import asyncio
from typing import List

from aiogram import F, Router, html
from aiogram.enums import MessageEntityType
from aiogram.filters import CommandStart
from aiogram.types import Chat, Message

from bot.filters import ChatType, HasUsernames
from bot.middlewares import LongOperation
from config import get_logger

logger = get_logger(__name__)

# Create routers
root_router = Router()
usernames_router = Router()

# Apply middleware to root router
root_router.message.middleware(LongOperation())


# Email handlers
@root_router.message(F.entities[:].type == MessageEntityType.EMAIL)
async def all_emails(message: Message):
    """Handle messages where all entities are emails."""
    await message.answer("All entities are emails")


@root_router.message(F.entities[...].type == MessageEntityType.EMAIL)
async def any_emails(message: Message):
    """Handle messages that contain at least one email."""
    await message.answer("At least one email!")


# Start command handler for groups/supergroups
@root_router.message(
    ChatType(chat_type=["group", "supergroup"]),
    CommandStart(),
    flags={"long_operation": "typing"},
)
async def command_start_handler(message: Message) -> None:
    """
    Handle /start command in groups and supergroups.
    """
    logger.debug("Chat info: %s", message.chat)

    if message.from_user is None:
        full_name = "Guest"
    else:
        full_name = message.from_user.first_name
        full_name += f" {message.from_user.last_name}" if message.from_user.last_name else ""

    await asyncio.sleep(2)
    await message.answer(f"Hello, {html.bold(full_name)}!")


# General text message handler
@root_router.message(F.text, flags={"long_operation": "typing"})
async def text_message_handler(message: Message) -> None:
    """Handle text messages with typing action."""
    if message.from_user is None:
        return

    logger.debug("Chat info: %s", message.chat)

    # Simulate processing time
    await asyncio.sleep(2)

    # For now, just echo back a simple response
    # TODO: Implement story-related functionality
    await message.answer(
        "Message received! Story functionality coming soon...",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


# Channel forwarding handler
@root_router.message(F.forward_from_chat[F.type == "channel"].as_("channel"))
async def forwarded_from_channel(message: Message, channel: Chat):
    """Handle messages forwarded from channels."""
    logger.debug("Channel forward - chat info: %s", message.chat)
    await message.answer(f"This channel's ID is {channel.id}")


# Username-specific handlers
@usernames_router.message(F.text, HasUsernames())
async def message_with_usernames(message: Message, usernames: List[str]):
    """Handle messages that contain usernames."""
    await message.reply(f"Found usernames: {', '.join(usernames)}")


def get_routers() -> List[Router]:
    """Get all bot routers."""
    return [root_router, usernames_router]
