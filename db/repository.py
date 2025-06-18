from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from config import get_logger
from db.models import (
    BlockedUser,
    BugReport,
    DownloadQueue,
    InvalidLinkViolation,
    Monitor,
    MonitorSentStory,
    ProfileRequest,
    Task,
    UserRequestLog,
)
from db.models import (
    Chat as ChatDB,
)
from db.models import (
    User as UserDB,
)
from db.schemas import Chat as ChatSchema
from db.schemas import Payment, Profile, Story, User, UserCreate

logger = get_logger(__name__)


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db


class UserRepository(BaseRepository):
    """Repository for user-related database operations."""

    def create_user(self, user: UserCreate) -> User:
        """Create a new user in the database."""
        logger.debug("Creating user with chat_id=%d, username=%s", user.chat_id, user.username)
        db_user = UserDB(
            chat_id=user.chat_id,
            username=user.username,
            is_bot=user.is_bot,
            is_premium=user.is_premium,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info("User created with id=%d", db_user.id)
        return User.model_validate(db_user)

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID from the database."""
        logger.info("Fetching user by id=%d", user_id)
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            return User.model_validate(db_user)
        return None

    def list_users(self) -> List[User]:
        """List all users in the database."""
        db_users = self.db.query(User).all()
        return [User.model_validate(u) for u in db_users]

    def add_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        return user

    def get_user_by_chat_id(self, chat_id: int):
        logger.info("Fetching user by chat_id=%d", chat_id)
        return self.db.query(User).filter_by(chat_id=chat_id).first()

    def list_all_users(self):
        return self.db.query(User).all()

    def block_user(self, chat_id: int, is_bot: bool = False) -> BlockedUser:
        """Block a user by their Telegram ID."""
        logger.debug("Blocking user with chat_id=%d, is_bot=%s", chat_id, is_bot)
        user = BlockedUser(
            chat_id=chat_id, is_bot=is_bot, blocked_at=int(datetime.now().timestamp())
        )
        self.db.add(user)
        self.db.commit()
        logger.info("User blocked with chat_id=%d", chat_id)
        return user

    def is_user_blocked(self, chat_id: int) -> bool:
        """Check if a user is blocked."""
        logger.debug("Checking if user is blocked with chat_id=%d", chat_id)
        result = self.db.query(BlockedUser).filter_by(chat_id=chat_id).first()
        return result is not None

    def is_user_temporarily_suspended(self, chat_id: int) -> bool:
        """Check if a user is temporarily suspended."""
        logger.debug("Checking if user is temporarily suspended with chat_id=%d", chat_id)
        violation = self.db.query(InvalidLinkViolation).filter_by(chat_id=chat_id).first()
        if not violation:
            return False
        now = int(datetime.now().timestamp())
        return bool(violation.suspended_until > now)

    def get_suspension_remaining(self, chat_id: int) -> int:
        """Get remaining suspension time in seconds."""
        logger.debug("Getting suspension remaining for chat_id=%d", chat_id)
        violation = self.db.query(InvalidLinkViolation).filter_by(chat_id=chat_id).first()
        if not violation:
            return 0
        now = int(datetime.now().timestamp())
        return max(0, violation.suspended_until - now)

    def save_user(self, user: UserCreate) -> User:
        """Save or update a user."""
        logger.info("Saving user with chat_id=%d", user.chat_id)
        existing = self.db.query(UserDB).filter_by(chat_id=user.chat_id).first()

        if existing:
            for key, value in user.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            logger.info("Updated existing user with chat_id=%d", user.chat_id)
            return User.model_validate(existing)
        else:
            db_user = UserDB(**user.model_dump())
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info("Created new user with chat_id=%d", user.chat_id)
            return User.model_validate(db_user)


class StoryRepository(BaseRepository):
    async def create(self, story: Story) -> Story:
        """Create a new story record."""
        data = story.model_dump()
        result = await self.db.table("stories").insert(data).execute()
        return Story(**result.data[0])

    async def get_by_id(self, story_id: int) -> Optional[Story]:
        """Get story by ID."""
        result = await self.db.table("stories").select("*").eq("id", story_id).execute()
        return Story(**result.data[0]) if result.data else None

    async def get_active_stories(self) -> List[Story]:
        """Get all active stories."""
        result = await self.db.table("stories").select("*").eq("is_viewed", False).execute()
        return [Story(**story) for story in result.data]


class ProfileRepository(BaseRepository):
    async def create(self, profile: Profile) -> Profile:
        """Create a new profile monitoring record."""
        data = profile.model_dump()
        result = await self.db.table("profiles").insert(data).execute()
        return Profile(**result.data[0])

    async def get_by_user_id(self, user_id: int) -> List[Profile]:
        """Get all profiles monitored by a user."""
        result = await self.db.table("profiles").select("*").eq("user_id", user_id).execute()
        return [Profile(**profile) for profile in result.data]

    async def update_last_check(self, profile_id: int) -> Profile:
        """Update the last check time for a profile."""
        data = {"last_check": datetime.now()}
        result = await self.db.table("profiles").update(data).eq("id", profile_id).execute()
        return Profile(**result.data[0])


class PaymentRepository(BaseRepository):
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment record."""
        data = payment.model_dump()
        result = await self.db.table("payments").insert(data).execute()
        return Payment(**result.data[0])

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.db.table("payments").select("*").eq("id", payment_id).execute()
        return Payment(**result.data[0]) if result.data else None

    async def get_by_user_id(self, user_id: int) -> List[Payment]:
        """Get all payments for a user."""
        result = await self.db.table("payments").select("*").eq("user_id", user_id).execute()
        return [Payment(**payment) for payment in result.data]


def add_blocked_user(session: Session, user: BlockedUser):
    session.add(user)
    session.commit()
    return user


def get_blocked_user(session: Session, chat_id: int):
    return session.query(BlockedUser).get(chat_id)


def list_blocked_users(session: Session):
    return session.query(BlockedUser).all()


def add_bug_report(session: Session, report: BugReport):
    session.add(report)
    session.commit()
    return report


def get_bug_report(session: Session, _id: int):
    return session.query(BugReport).get(_id)


def list_bug_reports(session: Session):
    return session.query(BugReport).all()


def add_download_queue(session: Session, queue: DownloadQueue):
    session.add(queue)
    session.commit()
    return queue


def get_download_queue(session: Session, _id: int):
    return session.query(DownloadQueue).get(_id)


def list_download_queues(session: Session):
    return session.query(DownloadQueue).all()


def add_invalid_link_violation(session: Session, violation: InvalidLinkViolation):
    session.add(violation)
    session.commit()
    return violation


def get_invalid_link_violation(session: Session, chat_id: int):
    return session.query(InvalidLinkViolation).get(chat_id)


def list_invalid_link_violations(session: Session):
    return session.query(InvalidLinkViolation).all()


def add_monitor_sent_story(session: Session, sent_story: MonitorSentStory):
    session.add(sent_story)
    session.commit()
    return sent_story


def list_monitor_sent_stories(session: Session):
    return session.query(MonitorSentStory).all()


def add_monitor(session: Session, monitor: Monitor):
    session.add(monitor)
    session.commit()
    return monitor


def get_monitor(session: Session, _id: int):
    return session.query(Monitor).get(_id)


def list_monitors(session: Session):
    return session.query(Monitor).all()


def add_profile_request(session: Session, request: ProfileRequest):
    session.add(request)
    session.commit()
    return request


def list_profile_requests(session: Session):
    return session.query(ProfileRequest).all()


def add_task(session: Session, task: Task):
    session.add(task)
    session.commit()
    return task


def get_task(session: Session, _id: str):
    return session.query(Task).get(_id)


def list_tasks(session: Session):
    return session.query(Task).all()


def add_user_request_log(session: Session, log: UserRequestLog):
    session.add(log)
    session.commit()
    return log


def list_user_request_logs(session: Session):
    return session.query(UserRequestLog).all()


def get_status_text() -> str:
    """Get admin status text."""
    return "Status not implemented yet."


class ChatRepository(BaseRepository):
    def create_chat(self, chat: ChatSchema) -> ChatSchema:
        db_chat = ChatDB(
            id=chat.id,
            type=chat.type,
            title=chat.title,
            username=chat.username,
            first_name=chat.first_name,
            last_name=chat.last_name,
            is_forum=chat.is_forum,
            created_at=chat.created_at,
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return ChatSchema.model_validate(db_chat)

    def try_create_chat(self, chat: ChatSchema) -> ChatSchema:
        """Try to create or update a chat record in the database.

        Args:
            chat: The chat schema to create or update

        Returns:
            The created or updated chat schema
        """
        logger.debug("Attempting to upsert chat with id=%d", chat.id)
        existing_chat = self.db.query(ChatDB).filter_by(id=chat.id).first()

        if existing_chat:
            logger.debug("Updating existing chat with id=%d", chat.id)
            for key, value in chat.model_dump().items():
                setattr(existing_chat, key, value)
            self.db.commit()
            self.db.refresh(existing_chat)
            return ChatSchema.model_validate(existing_chat)

        logger.debug("Creating new chat with id=%d", chat.id)
        return self.create_chat(chat)
