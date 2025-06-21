from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseSqlaModel


class User(BaseSqlaModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey("chat.id"), nullable=False, index=True)
    is_bot: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
