from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

from src.config.settings import Settings


async def start_bot(settings: Settings) -> None:
    """Start the Telegram bot."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Register handlers
    register_handlers(dp)

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Error in bot")
        raise
    finally:
        await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers."""
    # TODO: Implement handlers
    pass
