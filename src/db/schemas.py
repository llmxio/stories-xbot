from datetime import datetime
from typing import Optional

from aiogram.types import Chat as AiogramChat, Story as AiogramStory, User as AiogramUser
from pydantic import BaseModel, ConfigDict, Field


class ChatCreate(AiogramChat):
    """Chat create schema."""

    pass


class Chat(AiogramChat):
    model_config = ConfigDict(from_attributes=True, frozen=False)

    created_at: datetime = Field(default_factory=datetime.now)


class Story(AiogramStory):
    model_config = ConfigDict(from_attributes=True, frozen=False)


class UserBase(AiogramUser):
    model_config = ConfigDict(from_attributes=True, frozen=False)


class UserCreate(UserBase):
    chat_id: int = Field(..., description="Chat ID")


class User(UserBase):
    id: int = Field(..., description="User ID")
    is_blocked: bool = Field(default=False, description="Is blocked")
    blocked_at: Optional[datetime] = Field(default_factory=datetime.now, description="Blocked at")


# class Profile(BaseModel):
#     """Profile model for storing profile monitoring information."""

#     id: int = Field(..., description="Profile ID")
#     user_id: int = Field(..., description="User ID who is monitoring")
#     target_username: str = Field(..., description="Username being monitored")
#     target_phone: Optional[str] = Field(None, description="Phone number being monitored")
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: datetime = Field(default_factory=datetime.now)
#     is_active: bool = Field(default=True)
#     last_check: Optional[datetime] = Field(None, description="Last time the profile was checked")


# class Payment(BaseModel):
#     """Payment model for storing payment information."""

#     id: int = Field(..., description="Payment ID")
#     user_id: int = Field(..., description="User ID who made the payment")
#     amount: float = Field(..., description="Payment amount")
#     currency: str = Field(..., description="Payment currency")
#     status: str = Field(..., description="Payment status")
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: datetime = Field(default_factory=datetime.now)
#     transaction_id: Optional[str] = Field(None, description="Transaction ID")
#     payment_method: str = Field(..., description="Payment method used")


class BugReport(BaseModel):
    id: int = Field(..., description="Bug report ID")
    chat_id: int = Field(..., description="Chat ID")
    username: str = Field(..., description="Username")
    description: str = Field(..., description="Description")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at")

    model_config = ConfigDict(from_attributes=True)


class DownloadQueue(BaseModel):
    id: int = Field(..., description="Download queue ID")
    chat_id: int = Field(..., description="Chat ID")
    target_username: str = Field(..., description="Target username")
    status: str = Field(..., description="Status")
    enqueued_ts: datetime = Field(default_factory=datetime.now, description="Enqueued timestamp")
    processed_ts: Optional[datetime] = Field(None, description="Processed timestamp")
    error: Optional[str] = Field(None, description="Error message")
    task_details: Optional[str] = Field(None, description="Task details")

    model_config = ConfigDict(from_attributes=True)


class InvalidLinkViolation(BaseModel):
    chat_id: int = Field(..., description="Chat ID")
    count: int = Field(..., description="Count")
    suspended_until: datetime = Field(..., description="Suspended until")

    model_config = ConfigDict(from_attributes=True)


class MonitorSentStory(BaseModel):
    monitor_id: int = Field(..., description="Monitor ID")
    story_id: int = Field(..., description="Story ID")
    expires_at: datetime = Field(..., description="Expires at")

    model_config = ConfigDict(from_attributes=True)


class Monitor(BaseModel):
    id: int = Field(..., description="Monitor ID")
    chat_id: int = Field(..., description="Chat ID")
    target_username: str = Field(..., description="Target username")
    last_checked: datetime = Field(..., description="Last checked")
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class Task(BaseModel):
    id: str = Field(..., description="Task ID")
    chat_id: int = Field(..., description="Chat ID")
    status: str = Field(..., description="Status")
    task_details: str = Field(..., description="Task details")
    enqueued_ts: datetime = Field(default_factory=datetime.now, description="Enqueued timestamp")
    is_premium: int = Field(..., description="Is premium")
    is_bot: int = Field(..., description="Is bot")
    username: str = Field(..., description="Username")
    target_username: str = Field(..., description="Target username")
    description: str = Field(..., description="Description")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at")

    model_config = ConfigDict(from_attributes=True)
