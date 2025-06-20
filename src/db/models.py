import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChatType(str, enum.Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, index=True)
    type: Mapped[ChatType] = mapped_column(ENUM(ChatType, name="chat_type"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey("chat.id"), nullable=False, index=True)
    is_bot: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class BugReport(Base):
    __tablename__ = "bug_report"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True, index=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), index=True)
    username = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class DownloadQueue(Base):
    __tablename__ = "download_queue"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), nullable=False)
    target_username = sa.Column(sa.String)
    status = sa.Column(sa.String)
    enqueued_ts = sa.Column(sa.DateTime, default=datetime.now)
    processed_ts = sa.Column(sa.DateTime)
    error = sa.Column(sa.String)
    task_details = sa.Column(sa.String)


class InvalidLinkViolation(Base):
    __tablename__ = "invalid_link_violation"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), nullable=False)
    count = sa.Column(sa.Integer)
    suspended_until = sa.Column(sa.DateTime)


# class MonitorSentStory(Base):
#     __tablename__ = "monitor_sent_story"
#     monitor_id = sa.Column(
#         sa.BigInteger,
#         sa.ForeignKey("monitor.id"),
#         primary_key=True,
#     )
#     story_id = sa.Column(
#         sa.BigInteger,
#         sa.ForeignKey("story.id"),
#         primary_key=True,
#     )
#     expires_at = sa.Column(sa.DateTime)


class Monitor(Base):
    __tablename__ = "monitor"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"))
    target_username = sa.Column(sa.String)
    last_checked = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Story(Base):
    __tablename__ = "story"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    media_url = sa.Column(sa.String, nullable=False)
    is_viewed = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    expires_at = sa.Column(sa.DateTime, nullable=True)
    viewed_at = sa.Column(sa.DateTime, nullable=True)


class Task(Base):
    __tablename__ = "task"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
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
