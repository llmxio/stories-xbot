from loguru import logger
from pyrogram.client import Client

from config.settings import Settings


async def start_userbot(settings: Settings) -> None:
    """Start the Telegram userbot."""
    # Initialize userbot client
    app = Client(
        name=settings.userbot.session_name,
        api_id=settings.userbot.api_id,
        api_hash=settings.userbot.api_hash,
    )

    # Register handlers
    register_handlers(app)

    try:
        logger.info("Starting userbot...")
        await app.start()
        await app.idle()
    except Exception as e:
        logger.exception("Error in userbot")
        raise
    finally:
        await app.stop()


def register_handlers(app: Client) -> None:
    """Register all userbot handlers."""
    # TODO: Implement handlers
    pass
