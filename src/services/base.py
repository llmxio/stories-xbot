from typing import Any, Generic, Optional, Type, TypeVar, get_args

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_logger
from db.schemas import BaseModel
from models import BaseDbModel

T = TypeVar("T", bound=BaseDbModel)

log = get_logger(__name__)


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

        log.debug("Initializing BaseService with model=%s", model)

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

    # async def create(self, obj_model: BaseModel, **kwargs: Any) -> T:
    #     """Create a new user."""
    #     if not isinstance(obj_model, UserCreate):
    #         raise ValueError("Expected UserCreate instance")

    #     log.debug("Creating obj with chat_id=%d, objname=%s", obj.chat_id, obj.objname)

    #     obj_db = await super().create(
    #         obj,
    #         exclude_unset=True,
    #         exclude_none=True,
    #         exclude_defaults=True,
    #     )

    #     if user_db.id != 0:
    #         log.debug("User created with id=%d", user_db.id)
    #     else:
    #         self.session.add(user_db)
    #         await self.session.commit()
    #         await self.session.refresh(user_db)
    #         log.debug("User refreshed with id=%d", user_db.id)

    #     user_model = User.model_validate(user_db)
    #     # Cache the new user with status
    #     user_cache = UserCache.model_validate(user_model)
    #     user_cache.is_blocked = False
    #     # Note: is_suspended and suspension_remaining are not part of UserCache model
    #     # They should be handled separately or added to the model
    #     await user_cache.save_to_cache()
    #     return user_db
