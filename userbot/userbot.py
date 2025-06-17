import platform

import uvloop
from pyrogram import __version__ as PYROGRAM_VERSION
from pyrogram.client import Client
from pyrogram.sync import idle

from config import Config, get_logger

LOGGER = get_logger(__name__)


async def start_userbot(config: Config) -> None:
    """Start the Telegram userbot with interactive authentication and self-check."""
    # Use a fixed session file name for compatibility with the original project
    uvloop.install()

    app = Client(
        name=config.USERBOT_SESSION_NAME,
        api_id=config.USERBOT_API_ID,
        api_hash=config.USERBOT_API_HASH,
    )

    try:
        LOGGER.info("Starting userbot authentication (interactive mode)...")
        await app.start()

        me = await app.get_me()
        device_info = (
            f"Pyrogram v{PYROGRAM_VERSION} | "
            f"Python {platform.python_version()} | "
            f"Platform: {platform.system()} {platform.release()}"
        )

        msg = (
            f"✅ Userbot authenticated as: {me.first_name} (@{me.username}, id={me.id})\n"
            f"Device info: {device_info}"
        )
        await app.send_message("me", msg)

        LOGGER.info("Self-check message sent to Saved Messages: %s", msg)
        LOGGER.info("pyrogram key: %s", await app.export_session_string())

        await idle()
    except Exception as e:
        LOGGER.exception("Error during userbot authentication or self-check: %s", e)
        raise
    finally:
        await app.stop()


def register_handlers(app: Client) -> None:
    """Register all userbot handlers (not used in auth-only mode)."""
    pass


# if __name__ == "__main__":
#     import asyncio

#     from config import get_config

#     local_config = get_config()
#     asyncio.run(start_userbot(config=local_config))
