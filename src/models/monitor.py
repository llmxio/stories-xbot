from datetime import datetime

import sqlalchemy as sa

from .base import BaseSqlaModel


class Monitor(BaseSqlaModel):
    __tablename__ = "monitor"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    target_username = sa.Column(sa.String)
    last_checked = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
