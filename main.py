import asyncio

import uvloop

from bot.bot import start_bot
from config.config import Config, get_config
from config.logger import get_logger
from db.session import get_session
from userbot.userbot import start_userbot

LOGGER = get_logger(__name__)


async def main():
    # Load settings
    settings: Config = get_config()

    # Initialize database session
    session = get_session()

    # Start both bot and userbot
    bot_task = asyncio.create_task(start_bot(settings, session))
    userbot_task = asyncio.create_task(start_userbot(settings))

    try:
        await asyncio.gather(bot_task, userbot_task)
    except Exception as e:
        LOGGER.exception("Error in main loop: %s", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        uvloop.install()
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
