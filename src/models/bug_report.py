from datetime import datetime

import sqlalchemy as sa

from .base import Base


class BugReport(Base):
    __tablename__ = "bug_report"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True, index=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), index=True)
    username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
