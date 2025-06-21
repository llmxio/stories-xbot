from datetime import datetime

import sqlalchemy as sa

from .base import BaseDbModel


class DownloadQueue(BaseDbModel):
    __tablename__ = "download_queue"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), nullable=False)
    target_username = sa.Column(sa.String)
    status = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.DateTime, default=datetime.now)
    processed_ts = sa.Column(sa.DateTime)
    error = sa.Column(sa.String)
    task_details = sa.Column(sa.String)
