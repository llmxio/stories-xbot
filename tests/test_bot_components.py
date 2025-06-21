import asyncio

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.filters import ChatType, HasUsernames
from bot.handlers import get_routers
from bot.middlewares import LongOperation
from db.schemas import UserCreate
from db.session import get_session
from models import BaseDbModel, Chat, ChatType, User as UserDB
from services import UserService as UserService


@pytest.fixture(name="db_session", scope="function")
async def db_session_fixture():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(BaseDbModel.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine)
    session = session_maker()

    yield session
    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(BaseDbModel.metadata.drop_all)
    await engine.dispose()


def test_filters():
    """Test filter instantiation."""
    # Test ChatType filter
    chat_filter = ChatType("private")
    assert chat_filter.chat_type == "private"

    chat_filter_list = ChatType(["group", "supergroup"])
    assert chat_filter_list.chat_type == ["group", "supergroup"]

    # Test HasUsernames filter
    username_filter = HasUsernames()
    assert username_filter is not None

    print("✓ Filters test passed")


async def test_middlewares(session: AsyncSession):
    """Test middleware instantiation."""
    async with get_session() as session:
        middleware = LongOperation(session)
        assert middleware is not None
        print("✓ Middlewares test passed")


def test_handlers():
    """Test handlers structure."""
    routers = get_routers()
    assert len(routers) == 3
    assert all(hasattr(router, "include_router") for router in routers)
    print("✓ Handlers test passed")


if __name__ == "__main__":
    test_filters()
    asyncio.run(test_middlewares())
    test_handlers()
    print("🎉 All tests passed!")
