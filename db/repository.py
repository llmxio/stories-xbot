from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from db.models import (
    BlockedUser,
    BugReport,
    DownloadQueue,
    InvalidLinkViolation,
    Monitor,
    MonitorSentStory,
    ProfileRequest,
    Task,
    UserDB,
    UserRequestLog,
)

from db.schemas import Payment, Profile, Story, User, UserCreate


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db


class UserRepository(BaseRepository):
    """Repository for user-related database operations."""

    def create_user(self, user: UserCreate) -> User:
        """Create a new user in the database."""
        db_user = UserDB(
            telegram_id=user.telegram_id,
            username=user.username,
            email=user.email,
            password=user.password,
            created_at=datetime.now(),
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User.model_validate(db_user)

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID from the database."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            return User.model_validate(db_user)
        return None

    def list_users(self) -> List[User]:
        """List all users in the database."""
        db_users = self.db.query(UserDB).all()
        return [User.model_validate(u) for u in db_users]

    def add_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        return user

    def get_user_by_telegram_id(self, telegram_id: str):
        return self.db.query(User).get(telegram_id)

    def list_all_users(self):
        return self.db.query(User).all()

    def block_user(self, telegram_id: str, is_bot: bool = False) -> BlockedUser:
        """Block a user by their Telegram ID."""
        user = BlockedUser(
            telegram_id=telegram_id, is_bot=is_bot, blocked_at=int(datetime.now().timestamp())
        )
        self.db.add(user)
        self.db.commit()
        return user

    def is_user_blocked(self, telegram_id: str) -> bool:
        """Check if a user is blocked."""
        result = self.db.query(BlockedUser).filter_by(telegram_id=telegram_id).first()
        return result is not None

    def is_user_temporarily_suspended(self, telegram_id: str) -> bool:
        """Check if a user is temporarily suspended."""
        violation = self.db.query(InvalidLinkViolation).filter_by(telegram_id=telegram_id).first()
        if not violation:
            return False
        now = int(datetime.now().timestamp())
        return bool(violation.suspended_until > now)

    def get_suspension_remaining(self, telegram_id: str) -> int:
        """Get remaining suspension time in seconds."""
        violation = self.db.query(InvalidLinkViolation).filter_by(telegram_id=telegram_id).first()
        if not violation:
            return 0
        now = int(datetime.now().timestamp())
        return max(0, violation.suspended_until - now)

    def save_user(self, user: User) -> User:
        """Save or update a user."""
        existing = self.db.query(User).filter_by(telegram_id=str(user.id)).first()
        if existing:
            for key, value in user.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            return existing
        else:
            self.db.add(user)
            self.db.commit()
            return user


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


def get_blocked_user(session: Session, telegram_id: str):
    return session.query(BlockedUser).get(telegram_id)


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


def get_invalid_link_violation(session: Session, telegram_id: str):
    return session.query(InvalidLinkViolation).get(telegram_id)


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
