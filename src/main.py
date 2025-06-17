import asyncio
import logging
from pathlib import Path

from loguru import logger

from src.bot.bot import start_bot
from src.config.settings import load_settings
from src.userbot.userbot import start_userbot


async def main():
    # Load settings
    settings = load_settings()

    # Configure logging
    logger.add(
        Path("logs") / "bot.log", rotation="1 day", retention="7 days", level=settings.log_level
    )

    # Start both bot and userbot
    bot_task = asyncio.create_task(start_bot(settings))
    userbot_task = asyncio.create_task(start_userbot(settings))

    try:
        await asyncio.gather(bot_task, userbot_task)
    except Exception as e:
        logger.exception("Error in main loop")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Fatal error")
        raise
