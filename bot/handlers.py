"""Bot handlers for the Telegram bot."""

# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Local application imports
from bot.filters import IsAdmin, IsPremium
from bot.middlewares import LongOperation
from config import get_config, get_logger
from db.repository import (
    block_user,
    find_user_by_username,
    get_suspension_remaining,
    get_user_is_bot,
    is_user_blocked,
    is_user_temporarily_suspended,
    record_invalid_link,
    save_user,
    suspend_user_temp,
)
from db.session import get_session
from services.admin_stats import get_status_text
from services.monitor import (
    CHECK_INTERVAL_HOURS,
    add_profile_monitor,
    list_user_monitors,
    remove_profile_monitor,
)
from services.queue import get_queue_status_for_user, handle_new_task
from utils.helpers import is_valid_story_link, send_temporary_message
from utils.i18n import t

logger = get_logger(__name__)

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
# Middleware
# =============================
@root_router.message()
async def middleware_handler(message: Message) -> None:
    """Handle middleware checks for all messages."""
    if not message.from_user:
        return

    if message.from_user.is_bot:
        if message.from_user.id != get_config().BOT_ADMIN_ID:
            block_user(telegram_id=str(message.from_user.id), is_bot=True, session=get_session())
        return

    if is_user_blocked(telegram_id=str(message.from_user.id), session=get_session()):
        return

    if message.from_user.id != get_config().BOT_ADMIN_ID and is_user_temporarily_suspended(
        telegram_id=str(message.from_user.id), session=get_session()
    ):
        remaining = get_suspension_remaining(
            telegram_id=str(message.from_user.id), session=get_session()
        )
        minutes = (remaining + 59) // 60  # Ceiling division
        try:
            await message.answer(
                f"🚫 You are temporarily suspended for {minutes} minute{'s' if minutes != 1 else ''}."
            )
        except Exception as error:
            logger.error("Failed to send temporary message: %s", error)
        return

    await save_user(user=message.from_user, session=get_session())


# =============================
# Command Handlers
# =============================
@root_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle /start command."""
    if not message.from_user:
        return

    try:
        await save_user(message.from_user)
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


@root_router.message(Command("queue"))
async def command_queue_handler(message: Message) -> None:
    """Handle /queue command."""
    if not message.from_user:
        return

    locale = message.from_user.language_code or "en"
    msg = await get_queue_status_for_user(str(message.from_user.id))
    await send_temporary_message(message.bot, message.chat.id, msg)


@root_router.message(Command("profile"))
async def command_profile_handler(message: Message) -> None:
    """Handle /profile command."""
    if not message.from_user:
        return

    locale = message.from_user.language_code or "en"
    user = message.from_user

    # Helper to escape MarkdownV2 special characters
    def escape_md_v2(text: str) -> str:
        return text.replace(r"[\_*\[\]()~`>#+\-=|{}.!]", r"\\\1")

    # Compose profile info
    profile_info = [
        "*Your Telegram Profile:*",
        f"ID: `{escape_md_v2(str(user.id))}`",
        f"Name: {escape_md_v2(user.first_name)}"
        + (f" {escape_md_v2(user.last_name)}" if user.last_name else ""),
        f"Username: @{escape_md_v2(user.username)}" if user.username else None,
        f"Is Premium: {'Yes' if user.is_premium else 'No'}",
        f"Is Bot: {'Yes' if user.is_bot else 'No'}",
        f"Language: {escape_md_v2(user.language_code)}" if user.language_code else None,
    ]
    profile_text = "\n".join(filter(None, profile_info))
    await message.answer(profile_text, parse_mode="MarkdownV2")


# =============================
# Premium Commands
# =============================
@premium_router.message(Command("monitor"))
async def command_monitor_handler(message: Message) -> None:
    """Handle /monitor command."""
    if not message.from_user or not message.text:
        return

    locale = message.from_user.language_code or "en"
    user_id = str(message.from_user.id)
    args = message.text.split()[1:]

    if not args:
        monitors = await list_user_monitors(user_id)
        if not monitors:
            limit_msg = t(locale, "monitor.unlimited") + " "
            await message.answer(
                t(
                    locale,
                    "monitor.usage",
                    {
                        "limitMsg": limit_msg,
                        "hours": CHECK_INTERVAL_HOURS,
                    },
                )
            )
            return

        msg = t(
            locale,
            "monitor.list",
            {
                "count": len(monitors),
                "limit": "∞",
                "list": "\n".join(f"{i + 1}. @{m.target_username}" for i, m in enumerate(monitors)),
                "hours": CHECK_INTERVAL_HOURS,
            },
        )
        await message.answer(msg)
        return

    username = args[0].lstrip("@")
    await add_profile_monitor(user_id, username)
    remaining_text = t(locale, "monitor.unlimited")
    await message.answer(
        t(locale, "monitor.started", {"user": args[0], "remaining": remaining_text})
    )


@premium_router.message(Command("unmonitor"))
async def command_unmonitor_handler(message: Message) -> None:
    """Handle /unmonitor command."""
    if not message.from_user or not message.text:
        return

    locale = message.from_user.language_code or "en"
    user_id = str(message.from_user.id)
    args = message.text.split()[1:]

    if not args:
        monitors = await list_user_monitors(user_id)
        if not monitors:
            await message.answer(t(locale, "monitor.none"))
            return

        msg = t(
            locale,
            "monitor.current",
            {
                "list": "\n".join(f"{i + 1}. @{m.target_username}" for i, m in enumerate(monitors)),
            },
        )
        await message.answer(msg)
        return

    username = args[0].lstrip("@")
    await remove_profile_monitor(user_id, username)
    await message.answer(t(locale, "monitor.stopped", {"user": args[0]}))


# =============================
# Admin Commands
# =============================
@admin_router.message(Command("status"))
async def command_status_handler(message: Message) -> None:
    """Handle /status command."""
    text = get_status_text()
    await message.answer(text)


@admin_router.message(Command("restart"))
async def command_restart_handler(message: Message) -> None:
    """Handle /restart command."""
    if not message.from_user:
        return

    locale = message.from_user.language_code or "en"
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(locale, "admin.restartButton"),
        callback_data="restart",
    )
    await message.answer(
        t(locale, "admin.confirmRestart"),
        reply_markup=builder.as_markup(),
    )


@admin_router.message(Command("block"))
async def command_block_handler(message: Message) -> None:
    """Handle /block command."""
    if not message.from_user or not message.text:
        return

    locale = message.from_user.language_code or "en"
    args = message.text.split()[1:]

    if not args:
        await message.answer(t(locale, "admin.blockUsage"))
        return

    try:
        telegram_id: Optional[str] = None
        if args[0].startswith("@"):
            user = await find_user_by_username(args[0][1:])
            if not user:
                await message.answer(t(locale, "user.notFound"))
                return
            telegram_id = user.telegram_id
        elif args[0].isdigit():
            telegram_id = args[0]
        else:
            await message.answer(t(locale, "argument.invalid"))
            return

        is_bot = await get_user_is_bot(telegram_id)
        await block_user(telegram_id, is_bot)
        await message.answer(t(locale, "block.success", {"user": telegram_id}))
    except Exception as error:
        logger.error("Error in /block command: %s", error)
        await message.answer(t(locale, "error.generic"))


# =============================
# Callback Query Handlers
# =============================
@root_router.callback_query(F.data == "restart")
async def restart_callback_handler(callback: CallbackQuery) -> None:
    """Handle restart callback query."""
    if not callback.from_user or not callback.message or not callback.bot:
        return

    if callback.from_user.id != BOT_ADMIN_ID:
        return

    locale = callback.from_user.language_code or "en"
    await callback.answer(t(locale, "admin.restarting"))
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.bot.send_message(BOT_ADMIN_ID, t(locale, "admin.restarting"))
    # TODO: Implement proper restart mechanism
    # For now, just exit the process
    import sys

    sys.exit(0)


@root_router.callback_query(F.data.contains("&"))
async def story_callback_handler(callback: CallbackQuery) -> None:
    """Handle story-related callback queries."""
    if not callback.from_user or not callback.message or not callback.data:
        return

    username, next_stories_ids = callback.data.split("&")
    user = callback.from_user

    task = {
        "chat_id": str(user.id),
        "link": username,
        "link_type": "username",
        "next_stories_ids": next_stories_ids and eval(next_stories_ids),
        "locale": user.language_code or "",
        "user": user,
        "init_time": datetime.now().timestamp(),
        "is_premium": bool(user.is_premium),
        "story_request_type": "paginated",
        "is_paginated": True,
    }

    await handle_new_task(task)

    try:
        markup = callback.message.reply_markup
        if markup and markup.inline_keyboard:
            new_keyboard = [
                [btn for btn in row if btn.callback_data != callback.data]
                for row in markup.inline_keyboard
            ]
            new_keyboard = [row for row in new_keyboard if row]

            if new_keyboard:
                await callback.message.edit_reply_markup(
                    reply_markup={"inline_keyboard": new_keyboard}
                )
            else:
                try:
                    await callback.message.delete()
                except Exception:
                    pass
        else:
            await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as error:
        logger.error("Failed to update inline keyboard: %s", error)

    await callback.answer()


# =============================
# Text Message Handler
# =============================
@root_router.message(F.text)
async def text_message_handler(message: Message) -> None:
    """Handle text messages."""
    if not message.from_user or not message.text:
        return

    text = message.text
    user_id = message.from_user.id
    locale = message.from_user.language_code or "en"

    if user_id == BOT_ADMIN_ID and text == "restart":
        builder = InlineKeyboardBuilder()
        builder.button(
            text=t(locale, "admin.restartButton"),
            callback_data="restart",
        )
        await message.answer(
            t(locale, "admin.confirmRestart"),
            reply_markup=builder.as_markup(),
        )
        return

    is_story_link = is_valid_story_link(text)
    is_username = text.startswith("@") or text.startswith("+")
    looks_like_link = text.startswith(("http://", "https://")) or "t.me/" in text

    if is_username or is_story_link:
        task = {
            "chat_id": str(message.chat.id),
            "link": text,
            "link_type": "link" if is_story_link else "username",
            "locale": message.from_user.language_code or "",
            "user": message.from_user,
            "init_time": datetime.now().timestamp(),
            "is_premium": bool(message.from_user.is_premium),
        }
        await handle_new_task(task)
        return

    if looks_like_link and user_id != BOT_ADMIN_ID:
        count = await record_invalid_link(str(user_id))
        if count >= 5:
            await suspend_user_temp(str(user_id), 3600)
            await message.answer(t(locale, "invalidLink.suspended"))
        else:
            left = 5 - count
            await message.answer(t(locale, "invalidLink.warning", {"count": left}))
        return

    await message.answer(t(locale, "msg.invalidInput"), disable_web_page_preview=True)


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
