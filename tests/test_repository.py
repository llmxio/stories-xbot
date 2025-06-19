import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base
from db.repository import UserRepository
from db.schemas import UserCreate


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_and_get_user(db_session):
    repo = UserRepository(db_session)
    user_data = UserCreate(username="testuser", chat_id=12345, is_bot=False, is_premium=False)
    user = repo.create_user(user_data)
    assert user.username == "testuser"
    assert user.chat_id == 12345
    # Now get by id
    fetched = repo.get_user(user.id)
    assert fetched is not None
    assert fetched.username == "testuser"
    assert fetched.chat_id == 12345


def test_list_users(db_session):
    repo = UserRepository(db_session)
    user1 = repo.create_user(
        UserCreate(username="user1", chat_id=111, is_bot=False, is_premium=True)
    )
    user2 = repo.create_user(
        UserCreate(username="user2", chat_id=222, is_bot=False, is_premium=False)
    )
    users = repo.list_users()
    usernames = {u.username for u in users}
    assert "user1" in usernames
    assert "user2" in usernames
    assert user1.chat_id == 111
    assert user2.chat_id == 222
    assert len(users) == 2
