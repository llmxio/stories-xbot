from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from config import get_logger
from db.redis import UserCache
from db.schemas import User, UserCreate
from models import InvalidLinkViolation, User as UserDB

from .base import BaseService

log = get_logger(__name__)


class UserService(BaseService[UserDB]):
    """Service for user-related database operations."""

    async def create(self, user: UserCreate) -> UserDB:
        """Create a new user in the database."""
        if not isinstance(user, UserCreate):
            raise ValueError("Expected UserCreate instance")

        log.debug("Creating user with chat_id=%d, username=%s", user.chat_id, user.username)

        user_db = UserDB.model_validate(
            user.model_dump(
                exclude_unset=True,
                exclude_none=True,
                exclude_defaults=True,
            )
        )

        if user_db.id != 0:
            log.debug("User created with id=%d", user_db.id)
        else:
            self.session.add(user_db)
            await self.session.commit()
            await self.session.refresh(user_db)
            log.debug("User refreshed with id=%d", user_db.id)

        user_model = User.model_validate(user_db)
        # Cache the new user with status
        user_cache = UserCache.model_validate(user_model)
        user_cache.is_blocked = False
        # Note: is_suspended and suspension_remaining are not part of UserCache model
        # They should be handled separately or added to the model
        await user_cache.save_to_cache()
        return user_db

    async def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID from the database."""
        db_user = await self.session.get(UserDB, user_id)
        if db_user:
            return await self.get_user_by_chat_id(db_user.chat_id)
        return None

    async def get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
        """Retrieve a user by chat ID."""
        # Try to get from cache first
        cached_user = await UserCache.get_from_cache(chat_id)
        if cached_user:
            return cached_user

        # If not in cache, get from database
        log.debug("Cache miss, fetching user by chat_id=%d from database", chat_id)
        result = await self.session.execute(select(UserDB).filter_by(chat_id=chat_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            user = User.model_validate(db_user)
            # Cache the user with status
            cached_user = UserCache.model_validate(user)
            # Note: is_suspended and suspension_remaining are not part of UserCache model
            # They should be handled separately or added to the model
            await cached_user.save_to_cache()
            return user
        return None

    async def list_users(self) -> List[User]:
        """List all users in the database."""
        result = await self.session.execute(select(UserDB))
        db_users = result.scalars().all()
        return [User.model_validate(u) for u in db_users]

    async def add_user(self, user: User):
        self.session.add(user)
        await self.session.commit()
        return user

    async def list_all_users(self):
        result = await self.session.execute(select(UserDB))
        return result.scalars().all()

    def block_user(self, chat_id: int, is_blocked: bool):
        """Block a user by their Telegram ID."""
        log.warning(
            "Feature under development: block_user called with chat_id=%s and is_blocked=%s",
            chat_id,
            is_blocked,
        )

    # def block_user(self, chat_id: int, is_bot: bool = False) -> BlockedUser:
    #     """Block a user by their Telegram ID."""
    #     logger.debug("Blocking user with chat_id=%d, is_bot=%s", chat_id, is_bot)
    #     user = BlockedUser(
    #         chat_id=chat_id, is_bot=is_bot, blocked_at=int(datetime.now().timestamp())
    #     )
    #     self.db.add(user)
    #     self.db.commit()
    #     logger.info("User blocked with chat_id=%d", chat_id)

    #     # Update cache if exists
    #     cached_user = UserCache.get_from_cache(chat_id)
    #     if cached_user:
    #         cached_user.is_blocked = True
    #         cached_user.save_to_cache()

    #     return user

    # def is_user_blocked(self, chat_id: int) -> bool:
    #     """Check if a user is blocked."""
    #     logger.debug("Checking if user is blocked with chat_id=%d", chat_id)
    #     result = self.db.query(BlockedUser).filter_by(chat_id=chat_id).first()
    #     return result is not None

    async def is_user_temporarily_suspended(self, chat_id: int) -> bool:
        """Check if a user is temporarily suspended."""
        log.debug("Checking if user is temporarily suspended with chat_id=%d", chat_id)
        result = await self.session.execute(select(InvalidLinkViolation).filter_by(chat_id=chat_id))
        violation = result.scalar_one_or_none()
        if not violation:
            return False
        now = datetime.now()
        return bool(violation.suspended_until > now)

    async def get_suspension_remaining(self, chat_id: int) -> int:
        """Get remaining suspension time in seconds."""
        log.debug("Getting suspension remaining for chat_id=%d", chat_id)
        result = await self.session.execute(select(InvalidLinkViolation).filter_by(chat_id=chat_id))
        violation = result.scalar_one_or_none()
        if not violation:
            return 0
        now = datetime.now()
        remaining = (violation.suspended_until - now).total_seconds()
        return max(0, int(remaining))

    async def save_user(self, user: UserCreate) -> User:
        """Save or update a user."""
        log.debug("Saving user with chat_id=%d", user.chat_id)

        result = await self.session.execute(select(UserDB).filter_by(chat_id=user.chat_id))
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in user.model_dump().items():
                setattr(existing, key, value)
            await self.session.commit()
            log.debug("Updated existing user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(existing)
        else:
            db_user = UserDB(**user.model_dump())
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            log.debug("Created new user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(db_user)

        # Update cache with status
        cached_user = UserCache.model_validate(user_model)
        # Note: is_suspended and suspension_remaining are not part of UserCache model
        # They should be handled separately or added to the model
        await cached_user.save_to_cache()
        return user_model
