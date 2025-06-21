import asyncio

import uvloop

from bot import start_bot
from config import get_logger
from db.session import session_manager
from userbot import start_userbot

log = get_logger(__name__)


async def main():
    try:
        log.warning("Starting main loop")

        async with session_manager.session() as session:
            await asyncio.gather(
                asyncio.create_task(start_bot(session)),
                asyncio.create_task(start_userbot()),
            )

    except Exception as e:
        log.exception("Error in main loop: %s", e)
        raise


if __name__ == "__main__":
    try:
        uvloop.install()
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        log.warning("Main loop stopped")
