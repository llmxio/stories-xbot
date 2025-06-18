from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BlockedUser(Base):
    __tablename__ = "blocked_users"
    telegram_id = sa.Column(sa.String, primary_key=True)
    blocked_at = sa.Column(sa.Integer)
    is_bot = sa.Column(sa.Integer)


class BugReport(Base):
    __tablename__ = "bug_reports"
    id = sa.Column(sa.Integer, primary_key=True)
    telegram_id = sa.Column(sa.String)
    username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.Integer)


class DownloadQueue(Base):
    __tablename__ = "download_queue"
    id = sa.Column(sa.Integer, primary_key=True)
    telegram_id = sa.Column(sa.String)
    target_username = sa.Column(sa.String)
    status = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.Integer)
    processed_ts = sa.Column(sa.Integer)
    error = sa.Column(sa.String)
    task_details = sa.Column(sa.String)


class InvalidLinkViolation(Base):
    __tablename__ = "invalid_link_violations"
    telegram_id = sa.Column(sa.String, primary_key=True)
    count = sa.Column(sa.Integer)
    suspended_until = sa.Column(sa.Integer)


class MonitorSentStory(Base):
    __tablename__ = "monitor_sent_stories"
    monitor_id = sa.Column(sa.Integer, primary_key=True)
    story_id = sa.Column(sa.Integer, primary_key=True)
    expires_at = sa.Column(sa.Integer)


class Monitor(Base):
    __tablename__ = "monitors"
    id = sa.Column(sa.Integer, primary_key=True)
    telegram_id = sa.Column(sa.String)
    target_username = sa.Column(sa.String)
    last_checked = sa.Column(sa.Integer)
    created_at = sa.Column(sa.DateTime(timezone=True))


class ProfileRequest(Base):
    __tablename__ = "profile_requests"
    telegram_id = sa.Column(sa.String, primary_key=True)
    target_username = sa.Column(sa.String, primary_key=True)
    requested_at = sa.Column(sa.Integer)


class Task(Base):
    __tablename__ = "tasks"
    id = sa.Column(sa.String, primary_key=True)
    telegram_id = sa.Column(sa.String)
    status = sa.Column(sa.String)
    task_details = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.Integer)
    is_premium = sa.Column(sa.Integer)
    is_bot = sa.Column(sa.Integer)
    username = sa.Column(sa.String)
    target_username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.Integer)


class UserRequestLog(Base):
    __tablename__ = "user_request_log"
    telegram_id = sa.Column(sa.String, primary_key=True)
    requested_at = sa.Column(sa.Integer, primary_key=True)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = sa.Column(sa.String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
