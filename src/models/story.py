from datetime import datetime

import sqlalchemy as sa

from .base import BaseDbModel


class Story(BaseDbModel):
    __tablename__ = "story"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    media_url = sa.Column(sa.String, nullable=False)
    is_viewed = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    expires_at = sa.Column(sa.DateTime, nullable=True)
    viewed_at = sa.Column(sa.DateTime, nullable=True)
