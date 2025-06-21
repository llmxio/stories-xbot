import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.schemas import UserCreate
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


async def test_create_and_get_chat(db_session: AsyncSession):
    # First create the chat that the user will reference
    chat = Chat(id=12345, type=ChatType.PRIVATE)
    db_session.add(chat)
    await db_session.commit()

    # Query the chat from the database to verify it was created
    result = await db_session.execute(select(Chat).where(Chat.id == 12345))
    fetched_chat = result.scalar_one_or_none()

    assert fetched_chat is not None
    assert fetched_chat.id == 12345
    assert fetched_chat.type == ChatType.PRIVATE


async def test_list_chats(db_session: AsyncSession):
    # Create chats first
    chat1 = Chat(id=111, type=ChatType.PRIVATE)
    chat2 = Chat(id=222, type=ChatType.PRIVATE)
    db_session.add(chat1)
    db_session.add(chat2)
    await db_session.commit()

    # Query all chats from the database
    result = await db_session.execute(select(Chat))
    all_chats = result.scalars().all()

    # Verify we have 2 chats
    assert len(all_chats) == 2

    # Verify the chat IDs
    chat_ids = {chat.id for chat in all_chats}
    assert 111 in chat_ids
    assert 222 in chat_ids


async def test_user_repository_async_operations(db_session: AsyncSession):
    """Test that User repository operations work correctly with async drivers."""
    # Create a chat first (required for User foreign key)
    chat = Chat(id=99999, type=ChatType.PRIVATE)
    db_session.add(chat)
    await db_session.commit()

    # Create a user using the repository
    user_service = UserService(db_session)
    user_data = UserCreate(chat_id=99999, is_bot=False, is_premium=True, username="test", first_name="Test")
    user = await user_service.create(user_data)

    # Verify user was created correctly
    assert user.chat_id == 99999
    assert not user.is_bot
    assert user.is_premium
    assert user.id is not None

    # Test getting the user by ID
    fetched_user = await user_service.get(user.id)
    assert fetched_user is not None
    assert fetched_user.chat_id == 99999
    assert fetched_user.is_premium

    # Test listing users
    users = await user_service.list()
    assert len(users) == 1
    assert users[0].chat_id == 99999
