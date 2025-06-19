import asyncio

import uvloop

from bot.bot import start_bot
from config.config import Config, get_config
from config.logger import get_logger
from db.session import get_db_session
from userbot.userbot import start_userbot

LOGGER = get_logger(__name__)


async def main():
    # Load settings
    settings: Config = get_config()

    try:
        # Start both bot and userbot with session management
        with get_db_session() as session:
            bot_task = asyncio.create_task(start_bot(settings, session))
            userbot_task = asyncio.create_task(start_userbot(settings))
            await asyncio.gather(bot_task, userbot_task)
    except Exception as e:
        LOGGER.exception("Error in main loop: %s", e)
        raise


if __name__ == "__main__":
    try:
        uvloop.install()
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
