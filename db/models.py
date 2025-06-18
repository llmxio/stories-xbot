from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BlockedUser(Base):
    __tablename__ = "blocked_users"
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"), primary_key=True)
    blocked_at = sa.Column(sa.DateTime, default=datetime.now)
    is_bot = sa.Column(sa.Integer)


class BugReport(Base):
    __tablename__ = "bug_reports"
    id = sa.Column(sa.BigInteger, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"))
    username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class DownloadQueue(Base):
    __tablename__ = "download_queue"
    id = sa.Column(sa.BigInteger, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"))
    target_username = sa.Column(sa.String)
    status = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.DateTime, default=datetime.now)
    processed_ts = sa.Column(sa.DateTime)
    error = sa.Column(sa.String)
    task_details = sa.Column(sa.String)


class InvalidLinkViolation(Base):
    __tablename__ = "invalid_link_violations"
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"), primary_key=True)
    count = sa.Column(sa.Integer)
    suspended_until = sa.Column(sa.DateTime)


class MonitorSentStory(Base):
    __tablename__ = "monitor_sent_stories"
    monitor_id = sa.Column(sa.BigInteger, primary_key=True)
    story_id = sa.Column(sa.BigInteger, primary_key=True)
    expires_at = sa.Column(sa.DateTime)


class Monitor(Base):
    __tablename__ = "monitors"
    id = sa.Column(sa.BigInteger, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"))
    target_username = sa.Column(sa.String)
    last_checked = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class ProfileRequest(Base):
    __tablename__ = "profile_requests"
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"), primary_key=True)
    target_username = sa.Column(sa.String, primary_key=True)
    requested_at = sa.Column(sa.DateTime, default=datetime.now)


class Task(Base):
    __tablename__ = "tasks"
    id = sa.Column(sa.String, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"))
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


class UserRequestLog(Base):
    __tablename__ = "user_request_log"
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"), primary_key=True)
    requested_at = sa.Column(sa.DateTime, default=datetime.now, primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.BigInteger, primary_key=True, index=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chats.id"), index=True)
    username = sa.Column(sa.String, unique=True, index=True)
    is_bot = sa.Column(sa.Boolean, default=False, nullable=False)
    is_premium = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Chat(Base):
    __tablename__ = "chats"
    id = sa.Column(sa.BigInteger, primary_key=True)
    type = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=True)
    username = sa.Column(sa.String, nullable=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    is_forum = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
