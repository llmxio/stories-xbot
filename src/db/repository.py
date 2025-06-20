from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Base, Chat, Story, User
from .schemas import ChatCreate, StoryCreate, UserCreate

T = TypeVar("T", bound=Base)  # type: ignore[type-arg]


class Repository(Generic[T]):
    """Repository for data access."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Initialize repository."""
        self.session = session
        self.model = model

    async def get(self, pk: int) -> T | None:
        """Get a single record by primary key."""
        return await self.session.get(self.model, pk)

    async def list(self) -> list[T]:
        """Get all records."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())


class StoryRepository(Repository[Story]):
    """Story repository."""

    def __init__(self, session: AsyncSession):
        """Initialize story repository."""
        super().__init__(session, Story)

    async def create(self, story_data: StoryCreate) -> Story:
        """Create a new story."""
        story = Story(**story_data.model_dump())
        self.session.add(story)
        await self.session.commit()
        await self.session.refresh(story)
        return story


class UserRepository(Repository[User]):
    """User repository."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(session, User)

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class ChatRepository(Repository[Chat]):
    """Chat repository."""

    def __init__(self, session: AsyncSession):
        """Initialize chat repository."""
        super().__init__(session, Chat)

    async def get_or_create(self, chat_data: ChatCreate) -> Chat:
        """Get or create a chat."""
        chat = await self.session.get(Chat, chat_data.id)
        if chat:
            return chat

        chat = Chat(**chat_data.model_dump())
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat
