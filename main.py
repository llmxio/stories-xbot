import asyncio
import logging

# from bot.bot import start_bot
from config.logger import initialize_project_logger
from config.config import get_settings
from userbot.userbot import start_userbot

initialize_project_logger(__name__)
LOGGER = logging.getLogger(__name__)


async def main():
    # Load settings
    settings = get_settings()

    # Start both bot and userbot
    # bot_task = asyncio.create_task(start_bot(settings))
    userbot_task = asyncio.create_task(start_userbot(settings))

    try:
        # await asyncio.gather(bot_task, userbot_task)
        await asyncio.gather(userbot_task)
    except Exception as e:
        LOGGER.exception("Error in main loop: %s", e)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
