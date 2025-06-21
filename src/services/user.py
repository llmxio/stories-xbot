from datetime import datetime
from typing import List, Optional

from config import get_logger
from db.redis import CachedUser
from db.schemas import User, UserCreate
from models import InvalidLinkViolation, User as UserDB

from .base import BaseService

logger = get_logger(__name__)


class UserService(BaseService):
    """Service for user-related database operations."""

    async def create(self, user: UserCreate) -> User:
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
        user_model = User.model_validate(db_user)
        # Cache the new user with status
        cached_user = CachedUser.model_validate(user_model)
        cached_user.is_blocked = False
        cached_user.is_suspended = False
        cached_user.suspension_remaining = 0
        await cached_user.save_to_cache()
        return user_model

    async def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID from the database."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            return await self.get_user_by_chat_id(db_user.chat_id)
        return None

    async def get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
        """Retrieve a user by chat ID."""
        # Try to get from cache first
        cached_user = await CachedUser.get_from_cache(chat_id)
        if cached_user:
            return cached_user

        # If not in cache, get from database
        logger.debug("Cache miss, fetching user by chat_id=%d from database", chat_id)
        db_user = self.db.query(UserDB).filter_by(chat_id=chat_id).first()
        if db_user:
            user = User.model_validate(db_user)
            # Cache the user with status
            cached_user = CachedUser.model_validate(user)
            # cached_user.is_blocked = self.is_user_blocked(chat_id)
            cached_user.is_suspended = self.is_user_temporarily_suspended(chat_id)
            cached_user.suspension_remaining = self.get_suspension_remaining(chat_id)
            await cached_user.save_to_cache()
            return user
        return None

    def list_users(self) -> List[User]:
        """List all users in the database."""
        db_users = self.db.query(User).all()
        return [User.model_validate(u) for u in db_users]

    def add_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        return user

    def list_all_users(self):
        return self.db.query(User).all()

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
    #     cached_user = CachedUser.get_from_cache(chat_id)
    #     if cached_user:
    #         cached_user.is_blocked = True
    #         cached_user.save_to_cache()

    #     return user

    # def is_user_blocked(self, chat_id: int) -> bool:
    #     """Check if a user is blocked."""
    #     logger.debug("Checking if user is blocked with chat_id=%d", chat_id)
    #     result = self.db.query(BlockedUser).filter_by(chat_id=chat_id).first()
    #     return result is not None

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

    async def save_user(self, user: UserCreate) -> User:
        """Save or update a user."""
        logger.debug("Saving user with chat_id=%d", user.chat_id)
        existing = self.db.query(UserDB).filter_by(chat_id=user.chat_id).first()

        if existing:
            for key, value in user.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            logger.debug("Updated existing user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(existing)
        else:
            db_user = UserDB(**user.model_dump())
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.debug("Created new user with chat_id=%d", user.chat_id)
            user_model = User.model_validate(db_user)

        # Update cache with status
        cached_user = CachedUser.model_validate(user_model)
        # cached_user.is_blocked = self.is_user_blocked(user.chat_id)
        cached_user.is_suspended = self.is_user_temporarily_suspended(user.chat_id)
        cached_user.suspension_remaining = self.get_suspension_remaining(user.chat_id)
        await cached_user.save_to_cache()
        return user_model
