from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from config import get_logger
from db.redis import UserCache
from db.schemas import BaseModel, User, UserCreate
from models import InvalidLinkViolation, User as UserDB

from .base import BaseService

logger = get_logger(__name__)


class UserService(BaseService[UserDB]):
    """Service for user-related database operations."""

    async def create(self, user: BaseModel) -> UserDB:
        """Create a new user in the database."""
        if not isinstance(user, UserCreate):
            raise ValueError("Expected UserCreate instance")

        logger.debug("Creating user with chat_id=%d, username=%s", user.chat_id, user.username)

        db_user1 = await super().create(user)

        logger.debug("User created with id=%d", db_user1.id)

        db_user = UserDB(
            chat_id=user.chat_id,
            username=user.username,
            is_bot=user.is_bot,
            is_premium=user.is_premium,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        logger.info("User created with id=%d", db_user.id)
        user_model = User.model_validate(db_user)
        # Cache the new user with status
        cached_user = UserCache.model_validate(user_model)
        cached_user.is_blocked = False
        # Note: is_suspended and suspension_remaining are not part of UserCache model
        # They should be handled separately or added to the model
        await cached_user.save_to_cache()
        return db_user

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
        logger.debug("Cache miss, fetching user by chat_id=%d from database", chat_id)
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
        logger.warning(
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
        logger.debug("Checking if user is temporarily suspended with chat_id=%d", chat_id)
        result = await self.session.execute(select(InvalidLinkViolation).filter_by(chat_id=chat_id))
        violation = result.scalar_one_or_none()
        if not violation:
            return False
        now = datetime.now()
        return bool(violation.suspended_until > now)

    async def get_suspension_remaining(self, chat_id: int) -> int:
        """Get remaining suspension time in seconds."""
        logger.debug("Getting suspension remaining for chat_id=%d", chat_id)
        result = await self.session.execute(select(InvalidLinkViolation).filter_by(chat_id=chat_id))
        violation = result.scalar_one_or_none()
        if not violation:
            return 0
        now = datetime.now()
        remaining = (violation.suspended_until - now).total_seconds()
        return max(0, int(remaining))

    async def save_user(self, user: UserCreate) -> User:
        """Save or update a user."""
        logger.debug("Saving user with chat_id=%d", user.chat_id)
        result = await self.session.execute(select(UserDB).filter_by(chat_id=user.chat_id))
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in user.model_dump().items():
                setattr(existing, key, value)
            await self.session.commit()
            logger.debug("Updated existing user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(existing)
        else:
            db_user = UserDB(**user.model_dump())
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            logger.debug("Created new user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(db_user)

        # Update cache with status
        cached_user = UserCache.model_validate(user_model)
        # Note: is_suspended and suspension_remaining are not part of UserCache model
        # They should be handled separately or added to the model
        await cached_user.save_to_cache()
        return user_model
