# mypy: ignore-errors
# ruff: noqa
# pyright: ignore-all-errors

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# type: ignore
from config import get_logger
from db.redis import CachedUser
from db.schemas import User as UserSchema
from models import BaseDbModel, Chat, Story, UserDB  # type: ignore

logger = get_logger(__name__)


class UserRepository(BaseRepository[UserDB]):  # type: ignore
    """User repository."""

    # def __init__(self, session: Session):
    #     """Initialize user repository."""
    #     super().__init__(session, User)

    async def is_user_blocked(self, chat_id: int) -> bool:
        """Check if user is blocked."""
        user = await self.session.get(UserDB, chat_id)
        return user.is_blocked if user else False

    async def get_by_chat_id(self, chat_id: int) -> Optional[UserSchema]:
        """Retrieve a user by chat ID."""
        cached_user = await CachedUser.get_from_cache(chat_id)

        if cached_user:
            return cached_user

        logger.debug("Cache miss, fetching user by chat_id=%d from database", chat_id)
        db_user = await self.session.execute(select(UserDB).where(UserDB.chat_id == chat_id))

        if db_user:
            user = UserSchema.model_validate(db_user)
            # user.is_blocked = await self.is_user_blocked(chat_id)
            # user.is_suspended = await self.is_user_temporarily_suspended(chat_id)
            # user.suspension_remaining = await self.get_suspension_remaining(chat_id)
            # Cache the user with status
            cached_user = CachedUser.model_validate(user)
            await cached_user.save_to_cache()
            return user

        return None


class StoryRepository(BaseRepository[Story]):  # type: ignore
    """Story repository."""

    def __init__(self, session: AsyncSession):
        """Initialize story repository."""
        super().__init__(session, Story)

    # async def create(self, story_data: StoryCreate) -> Story:
    #     """Create a new story."""
    #     story = Story(**story_data.model_dump())
    #     self.session.add(story)
    #     await self.session.commit()
    #     await self.session.refresh(story)
    #     return story


class ChatRepository(BaseRepository[Chat]):  # type: ignore
    """Chat repository."""

    def __init__(self, session: AsyncSession):
        """Initialize chat repository."""
        super().__init__(session, Chat)

    # async def get_or_create(self, chat_data: ChatCreate) -> Chat:
    #     """Get or create a chat."""
    #     chat = await self.session.get(Chat, chat_data.id)

    #     if chat:
    #         return chat

    #     chat = Chat(**chat_data.model_dump())
    #     self.session.add(chat)
    #     await self.session.commit()
    #     await self.session.refresh(chat)
    #     return chat
