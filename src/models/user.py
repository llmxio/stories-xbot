from datetime import datetime
from typing import Type, TypeVar

import sqlalchemy as sa
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDbModel

T = TypeVar("T", bound="User")


class User(BaseDbModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey("chat.id"), nullable=False, index=True)
    is_bot: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    language_code: Mapped[str] = mapped_column(nullable=True)

    added_to_attachment_menu: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_join_groups: Mapped[bool] = mapped_column(default=True, nullable=False)
    can_read_all_group_messages: Mapped[bool] = mapped_column(default=False, nullable=False)
    supports_inline_queries: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_connect_to_business: Mapped[bool] = mapped_column(default=False, nullable=False)
    has_main_web_app: Mapped[bool] = mapped_column(default=False, nullable=False)

    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    blocked_at: Mapped[datetime] = mapped_column(default=None, nullable=True)

    @classmethod
    def from_schema(
        cls: Type[T],
        user_schema: BaseModel,
        validate: bool = True,
    ) -> T:
        """
        Safely create UserDB from schema with optional validation.

        Args:
            user_schema: Pydantic schema instance
            validate: Whether to validate the data before creation

        Returns:
            UserDB instance

        Raises:
            ValidationError: If validation fails and validate=True
        """
        field_mapping = {
            "chat_id": getattr(user_schema, "chat_id"),
            "is_bot": getattr(user_schema, "is_bot"),
            "is_premium": getattr(user_schema, "is_premium", False),
            "first_name": getattr(user_schema, "first_name"),
            "last_name": getattr(user_schema, "last_name", None),
            "username": getattr(user_schema, "username", None),
            "language_code": getattr(user_schema, "language_code", None),
            "added_to_attachment_menu": getattr(user_schema, "added_to_attachment_menu", False),
            "can_join_groups": getattr(user_schema, "can_join_groups", True),
            "can_read_all_group_messages": getattr(user_schema, "can_read_all_group_messages", False),
            "supports_inline_queries": getattr(user_schema, "supports_inline_queries", False),
            "can_connect_to_business": getattr(user_schema, "can_connect_to_business", False),
            "has_main_web_app": getattr(user_schema, "has_main_web_app", False),
            "created_at": getattr(user_schema, "created_at", datetime.now()),
            "is_blocked": getattr(user_schema, "is_blocked", False),
            "blocked_at": getattr(user_schema, "blocked_at", None),
        }

        # Filter out None values for optional fields
        filtered_fields = {k: v for k, v in field_mapping.items() if v is not None}

        filtered_fields = user_schema.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude_defaults=True,
        )

        return cls(**filtered_fields)
