from typing import Generic, Optional, Type, TypeVar, get_args

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_logger
from db.schemas import BaseModel
from models import BaseSqlaModel

T = TypeVar("T", bound=BaseSqlaModel)

logger = get_logger(__name__)


class BaseService(Generic[T]):
    """Repository for data access."""

    model: Type[T]

    def __init__(self, session: AsyncSession, model: Optional[Type[T]] = None):
        """Initialize repository."""
        self.session = session

        if model is None:
            # Try to infer from generic type
            orig_bases = getattr(self.__class__, "__orig_bases__", ())
            if orig_bases:
                model = get_args(orig_bases[0])[0]

        logger.debug("Initializing BaseService with model=%s", model)

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
