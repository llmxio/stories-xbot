from typing import Generic, Optional, Type, TypeVar, get_args

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from .models import Base, Chat, Story, User

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Repository for data access."""

    # model: Type[T]

    def __init__(self, session: Session, model: Optional[Type[T]] = None):
        """Initialize repository."""
        self.session = session
        if model is None:
            # Try to infer from generic type
            orig_bases = getattr(self.__class__, "__orig_bases__", ())
            if orig_bases:
                model = get_args(orig_bases[0])[0]
        if model:
            self.model = model
        else:
            raise ValueError("Model is not specified")

    async def get(self, pk: int) -> Optional[T]:
        """Get a single record by primary key."""
        return await self.session.get(self.model, pk)

    async def list(self) -> list[T]:
        """Get all records."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, schema: BaseModel) -> T:
        """Create a new user."""
        db_obj = self.model(**schema.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj


class UserRepository(BaseRepository[User]):
    """User repository."""

    # def __init__(self, session: Session):
    #     """Initialize user repository."""
    #     super().__init__(session, User)

    # async def create(self, user_data: UserSchema) -> User:
    #     """Create a new user."""
    #     user = User(**user_data.model_dump())
    #     self.session.add(user)
    #     await self.session.commit()
    #     await self.session.refresh(user)
    #     return user


class StoryRepository(BaseRepository[Story]):
    """Story repository."""

    def __init__(self, session: Session):
        """Initialize story repository."""
        super().__init__(session, Story)

    # async def create(self, story_data: StoryCreate) -> Story:
    #     """Create a new story."""
    #     story = Story(**story_data.model_dump())
    #     self.session.add(story)
    #     await self.session.commit()
    #     await self.session.refresh(story)
    #     return story


class ChatRepository(BaseRepository[Chat]):
    """Chat repository."""

    def __init__(self, session: Session):
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
