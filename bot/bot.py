from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config, get_logger

LOGGER = get_logger(__name__)


async def start_bot(settings: Config) -> None:
    """Start the Telegram bot."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register handlers
    register_handlers(dp)

    try:
        LOGGER.info("Starting bot...")
        await dp.start_polling(bot)  # type: ignore
    except Exception as e:
        LOGGER.exception("Error in bot: %s", e)
        raise
    finally:
        await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers."""
    # TODO: Implement handlers
