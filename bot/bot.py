from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.orm import Session

from bot.handlers import get_routers
from bot.middlewares import LoggingMiddleware, LongOperation, UserMiddleware
from config import Config, get_logger

LOGGER = get_logger(__name__)


async def start_bot(settings: Config, session: Session) -> None:
    """Start the Telegram bot."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register handlers
    register_handlers(dp)

    # Initialize middlewares
    dp.update.middleware(UserMiddleware(session))
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(LongOperation())

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
    routers = get_routers()
    for router in routers:
        dp.include_router(router)
    LOGGER.info("Registered %d routers", len(routers))
