from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from supabase import Client

from .models import (
    BlockedUser,
    BugReport,
    DownloadQueue,
    InvalidLinkViolation,
    Monitor,
    MonitorSentStory,
    ProfileRequest,
    Task,
    User,
    UserRequestLog,
)
from .schemas import Payment, Profile, Story


class BaseRepository:
    def __init__(self, client: Client):
        self.client = client


class UserRepository(BaseRepository):
    async def create(self, user: User) -> User:
        """Create a new user."""
        data = user.model_dump()
        result = await self.client.table("users").insert(data).execute()
        return User(**result.data[0])

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.client.table("users").select("*").eq("id", user_id).execute()
        return User(**result.data[0]) if result.data else None

    async def update(self, user: User) -> User:
        """Update user information."""
        data = user.model_dump()
        result = await self.client.table("users").update(data).eq("id", user.id).execute()
        return User(**result.data[0])


class StoryRepository(BaseRepository):
    async def create(self, story: Story) -> Story:
        """Create a new story record."""
        data = story.model_dump()
        result = await self.client.table("stories").insert(data).execute()
        return Story(**result.data[0])

    async def get_by_id(self, story_id: int) -> Optional[Story]:
        """Get story by ID."""
        result = await self.client.table("stories").select("*").eq("id", story_id).execute()
        return Story(**result.data[0]) if result.data else None

    async def get_active_stories(self) -> List[Story]:
        """Get all active stories."""
        result = await self.client.table("stories").select("*").eq("is_viewed", False).execute()
        return [Story(**story) for story in result.data]


class ProfileRepository(BaseRepository):
    async def create(self, profile: Profile) -> Profile:
        """Create a new profile monitoring record."""
        data = profile.model_dump()
        result = await self.client.table("profiles").insert(data).execute()
        return Profile(**result.data[0])

    async def get_by_user_id(self, user_id: int) -> List[Profile]:
        """Get all profiles monitored by a user."""
        result = await self.client.table("profiles").select("*").eq("user_id", user_id).execute()
        return [Profile(**profile) for profile in result.data]

    async def update_last_check(self, profile_id: int) -> Profile:
        """Update the last check time for a profile."""
        data = {"last_check": datetime.utcnow()}
        result = await self.client.table("profiles").update(data).eq("id", profile_id).execute()
        return Profile(**result.data[0])


class PaymentRepository(BaseRepository):
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment record."""
        data = payment.model_dump()
        result = await self.client.table("payments").insert(data).execute()
        return Payment(**result.data[0])

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.client.table("payments").select("*").eq("id", payment_id).execute()
        return Payment(**result.data[0]) if result.data else None

    async def get_by_user_id(self, user_id: int) -> List[Payment]:
        """Get all payments for a user."""
        result = await self.client.table("payments").select("*").eq("user_id", user_id).execute()
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


def add_user(session: Session, user: User):
    session.add(user)
    session.commit()
    return user


def get_user(session: Session, telegram_id: str):
    return session.query(User).get(telegram_id)


def list_users(session: Session):
    return session.query(User).all()


def block_user(session: Session, telegram_id: str, is_bot: bool = False) -> BlockedUser:
    """Block a user by their Telegram ID."""
    user = BlockedUser(
        telegram_id=telegram_id, is_bot=is_bot, blocked_at=int(datetime.utcnow().timestamp())
    )
    session.add(user)
    session.commit()
    return user


def is_user_blocked(session: Session, telegram_id: str) -> bool:
    """Check if a user is blocked."""
    result = session.query(BlockedUser).filter_by(telegram_id=telegram_id).first()
    return result is not None


def is_user_temporarily_suspended(session: Session, telegram_id: str) -> bool:
    """Check if a user is temporarily suspended."""
    violation = session.query(InvalidLinkViolation).filter_by(telegram_id=telegram_id).first()
    if not violation:
        return False
    # Check if suspension period has passed
    now = int(datetime.utcnow().timestamp())
    return violation.suspended_until > now


def get_suspension_remaining(session: Session, telegram_id: str) -> int:
    """Get remaining suspension time in seconds."""
    violation = session.query(InvalidLinkViolation).filter_by(telegram_id=telegram_id).first()
    if not violation:
        return 0
    now = int(datetime.utcnow().timestamp())
    return max(0, violation.suspended_until - now)


def save_user(session: Session, user: User) -> User:
    """Save or update a user."""
    existing = session.query(User).filter_by(telegram_id=str(user.id)).first()
    if existing:
        for key, value in user.model_dump().items():
            setattr(existing, key, value)
        session.commit()
        return existing
    else:
        session.add(user)
        session.commit()
        return user
