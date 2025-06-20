from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BugReport(Base):
    __tablename__ = "bug_report"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class DownloadQueue(Base):
    __tablename__ = "download_queue"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    target_username = sa.Column(sa.String)
    status = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.DateTime, default=datetime.now)
    processed_ts = sa.Column(sa.DateTime)
    error = sa.Column(sa.String)
    task_details = sa.Column(sa.String)


class InvalidLinkViolation(Base):
    __tablename__ = "invalid_link_violation"
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), primary_key=True)
    count = sa.Column(sa.Integer)
    suspended_until = sa.Column(sa.DateTime)


class MonitorSentStory(Base):
    __tablename__ = "monitor_sent_story"
    monitor_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("monitor.id"),
        primary_key=True,
    )
    story_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("story.id"),
        primary_key=True,
    )
    expires_at = sa.Column(sa.DateTime)


class Monitor(Base):
    __tablename__ = "monitor"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    target_username = sa.Column(sa.String)
    last_checked = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Story(Base):
    __tablename__ = "story"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"), nullable=False)
    media_url = sa.Column(sa.String, nullable=False)
    is_viewed = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    expires_at = sa.Column(sa.DateTime, nullable=True)
    viewed_at = sa.Column(sa.DateTime, nullable=True)


class Task(Base):
    __tablename__ = "task"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    status = sa.Column(sa.String)
    task_details = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.DateTime, default=datetime.now)
    is_premium = sa.Column(sa.Integer)
    is_bot = sa.Column(sa.Integer)
    username = sa.Column(sa.String)
    target_username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    username = sa.Column(sa.String, unique=True, index=True)
    is_bot = sa.Column(sa.Boolean, default=False, nullable=False)
    is_premium = sa.Column(sa.Boolean, default=False, nullable=False)
    is_blocked = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Chat(Base):
    __tablename__ = "chat"
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    type = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=True)
    username = sa.Column(sa.String, nullable=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
