from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession as Session

from bot.handlers import get_routers
from bot.middlewares import LoggingMiddleware, LongOperation, UserMiddleware
from config import get_config, get_logger

LOG_LEVEL = get_config().LOG_LEVEL

LOG = get_logger(__name__)


async def start_bot(session: Session) -> None:
    """Start the Telegram bot."""

    config = get_config()

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Initialize middlewares
    dp.message.middleware(UserMiddleware(session))
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(LongOperation())

    # Register handlers
    register_handlers(dp)

    try:
        LOG.debug("Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)  # type: ignore
    except Exception as e:
        LOG.exception("Error in bot: %s", e)
        raise
    finally:
        await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers."""
    routers = get_routers()
    for router in routers:
        dp.include_router(router)
    LOG.info("Registered %d routers", len(routers))
