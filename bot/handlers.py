"""Bot handlers for the Telegram bot."""

# Standard library imports
from typing import List

# Third-party imports
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# Local application imports
from bot.filters import IsAdmin, IsPremium
from bot.middlewares import LongOperation
from config import get_logger

logger = get_logger(__name__)

# Temporary placeholder for BOT_ADMIN_ID and t
BOT_ADMIN_ID = 0

t = lambda locale, key, *args, **kwargs: key  # Dummy translation function

# Create routers
root_router = Router()
admin_router = Router()
premium_router = Router()

# Apply middleware to root router
root_router.message.middleware(LongOperation())

# Apply filters
admin_router.message.filter(IsAdmin())
premium_router.message.filter(IsPremium())


# =============================
# Command Handlers
# =============================
@root_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle /start command."""
    if not message.from_user:
        return

    try:
        # await save_user(message.from_user)  # Not implemented
        pass
        logger.info("User %d started the bot", message.from_user.id)
    except Exception as error:
        logger.error("Failed to save user on /start: %s", error)

    locale = message.from_user.language_code or "en"
    is_admin = message.from_user.id == BOT_ADMIN_ID
    is_premium = message.from_user.is_premium or False

    msg = t(locale, "start.instructions")
    await message.answer(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    # Update commands based on user type
    await update_user_commands(message, is_admin, is_premium)


@root_router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """Handle /help command."""
    if not message.from_user:
        return

    locale = message.from_user.language_code or "en"
    is_admin = message.from_user.id == BOT_ADMIN_ID
    is_premium = message.from_user.is_premium or False

    help_text = t(locale, "help.header") + "\n\n"
    help_text += t(
        locale,
        "help.general",
        {
            "cmdStart": t(locale, "cmd.start"),
            "cmdHelp": t(locale, "cmd.help"),
            "cmdQueue": t(locale, "cmd.queue"),
            "cmdProfile": t(locale, "cmd.profile"),
            "cmdMonitor": t(locale, "cmd.monitor"),
            "cmdUnmonitor": t(locale, "cmd.unmonitor"),
            "cmdBugs": t(locale, "cmd.bugs"),
        },
    )

    if is_admin:
        help_text += "\n" + t(
            locale,
            "help.admin",
            {
                "cmdUsers": t(locale, "cmd.users"),
                "cmdHistory": t(locale, "cmd.history"),
                "cmdBlock": t(locale, "cmd.block"),
                "cmdUnblock": t(locale, "cmd.unblock"),
                "cmdBlocklist": t(locale, "cmd.blocklist"),
                "cmdRestart": t(locale, "cmd.restart"),
                "cmdStatus": t(locale, "cmd.status"),
                "cmdListbugs": t(locale, "cmd.listbugs"),
            },
        )

    await message.answer(help_text, parse_mode="Markdown")
    await update_user_commands(message, is_admin, is_premium)


# =============================
# All other handlers: Not implemented
# =============================


@root_router.message()
async def not_implemented_handler(message: Message) -> None:
    await message.answer("Not implemented!!!")


@premium_router.message()
async def not_implemented_premium_handler(message: Message) -> None:
    await message.answer("Not implemented!!!")


@admin_router.message()
async def not_implemented_admin_handler(message: Message) -> None:
    await message.answer("Not implemented!!!")


# =============================
# Helper Functions
# =============================
async def update_user_commands(message: Message, is_admin: bool, is_premium: bool) -> None:
    """Update user commands based on their status."""
    if not message.from_user or not message.bot:
        return

    locale = message.from_user.language_code or "en"
    commands = []

    # Base commands
    commands.extend(
        [
            ("start", t(locale, "cmd.start")),
            ("help", t(locale, "cmd.help")),
            ("queue", t(locale, "cmd.queue")),
            ("profile", t(locale, "cmd.profile")),
            ("bugs", t(locale, "cmd.bugs")),
        ]
    )

    # Premium commands
    if is_premium or is_admin:
        commands.extend(
            [
                ("monitor", t(locale, "cmd.monitor")),
                ("unmonitor", t(locale, "cmd.unmonitor")),
            ]
        )

    # Admin commands
    if is_admin:
        commands.extend(
            [
                ("users", t(locale, "cmd.users")),
                ("history", t(locale, "cmd.history")),
                ("block", t(locale, "cmd.block")),
                ("unblock", t(locale, "cmd.unblock")),
                ("blocklist", t(locale, "cmd.blocklist")),
                ("status", t(locale, "cmd.status")),
                ("restart", t(locale, "cmd.restart")),
                ("bugreport", t(locale, "cmd.listbugs")),
                ("bugs", t(locale, "cmd.bugs")),
                ("reset_auth", "Reset Telegram auth code"),
                ("flush", t(locale, "cmd.flush")),
                ("welcome", t(locale, "cmd.welcome")),
            ]
        )

    await message.bot.set_my_commands(
        commands,
        scope={"type": "chat", "chat_id": message.chat.id},
    )


def get_routers() -> List[Router]:
    """Get all bot routers."""
    return [root_router, admin_router, premium_router]
