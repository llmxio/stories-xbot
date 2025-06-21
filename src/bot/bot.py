from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers import get_routers
from bot.middlewares import LoggingMiddleware, LongOperation, UserMiddleware
from config import get_config, get_logger

log = get_logger(__name__)


async def start_bot(session: AsyncSession) -> None:
    """Start the Telegram bot."""

    config = get_config()

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Initialize middlewares
    dp.message.middleware(UserMiddleware(session))
    dp.message.middleware(LoggingMiddleware(session))
    dp.message.middleware(LongOperation(session))

    # Register handlers
    register_handlers(dp)

    try:
        log.warning("Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)  # type: ignore
    except Exception as e:
        log.exception("Error in bot: %s", e)
        raise
    finally:
        await bot.session.close()
        log.warning("Stopped bot...")


def register_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers."""
    routers = get_routers()
    for router in routers:
        dp.include_router(router)
    log.info("Registered %d routers", len(routers))
