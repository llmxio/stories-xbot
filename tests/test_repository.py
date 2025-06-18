import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base
from db.repository import UserRepository
from db.schemas import User, UserCreate


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
    user_data = UserCreate(
        username="testuser", email="test@example.com", password="secret", telegram_id="tgid1"
    )
    user = repo.create_user(user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    # Now get by id
    fetched = repo.get_user(user.id)
    assert fetched is not None
    assert fetched.username == "testuser"
    assert fetched.email == "test@example.com"


def test_list_users(db_session):
    repo = UserRepository(db_session)
    user1 = repo.create_user(
        UserCreate(username="user1", email="u1@example.com", password="pw1", telegram_id="tgid2")
    )

    user2 = repo.create_user(
        UserCreate(username="user2", email="u2@example.com", password="pw2", telegram_id="tgid3")
    )
    assert user1.telegram_id == "tgid2"
    assert user2.telegram_id == "tgid3"

    users = repo.list_users()
    usernames = {u.username for u in users}

    assert "user1" in usernames
    assert "user2" in usernames
    assert len(users) == 2
