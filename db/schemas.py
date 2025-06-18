from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Story(BaseModel):
    """Story model for storing story information."""

    id: int = Field(..., description="Story ID")
    user_id: int = Field(..., description="User ID who posted the story")
    media_url: str = Field(..., description="URL to the story media")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(None, description="Story expiration time")
    is_viewed: bool = Field(default=False)
    viewed_at: Optional[datetime] = Field(None, description="When the story was viewed")


class Profile(BaseModel):
    """Profile model for storing profile monitoring information."""

    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID who is monitoring")
    target_username: str = Field(..., description="Username being monitored")
    target_phone: Optional[str] = Field(None, description="Phone number being monitored")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    last_check: Optional[datetime] = Field(None, description="Last time the profile was checked")


class Payment(BaseModel):
    """Payment model for storing payment information."""

    id: int = Field(..., description="Payment ID")
    user_id: int = Field(..., description="User ID who made the payment")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")
    status: str = Field(..., description="Payment status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    payment_method: str = Field(..., description="Payment method used")


class UserBase(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")


class UserCreate(UserBase):
    password: str = Field(..., description="Password")


class User(UserBase):
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class BlockedUser(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID")
    blocked_at: int = Field(..., description="Blocked at")
    is_bot: int = Field(..., description="Is bot")

    class Config:
        from_attributes = True


class BugReport(BaseModel):
    id: int = Field(..., description="Bug report ID")
    telegram_id: str = Field(..., description="Telegram ID")
    username: str = Field(..., description="Username")
    description: str = Field(..., description="Description")
    created_at: int = Field(..., description="Created at")

    class Config:
        from_attributes = True


class DownloadQueue(BaseModel):
    id: int = Field(..., description="Download queue ID")
    telegram_id: str = Field(..., description="Telegram ID")
    target_username: str = Field(..., description="Target username")
    status: str = Field(..., description="Status")
    enqueued_ts: int = Field(..., description="Enqueued timestamp")
    processed_ts: int = Field(..., description="Processed timestamp")
    error: str = Field(..., description="Error")
    task_details: str = Field(..., description="Task details")

    class Config:
        from_attributes = True


class InvalidLinkViolation(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID")
    count: int = Field(..., description="Count")
    suspended_until: int = Field(..., description="Suspended until")

    class Config:
        from_attributes = True


class MonitorSentStory(BaseModel):
    monitor_id: int = Field(..., description="Monitor ID")
    story_id: int = Field(..., description="Story ID")
    expires_at: int = Field(..., description="Expires at")

    class Config:
        from_attributes = True


class Monitor(BaseModel):
    id: int = Field(..., description="Monitor ID")
    telegram_id: str = Field(..., description="Telegram ID")
    target_username: str = Field(..., description="Target username")
    last_checked: int = Field(..., description="Last checked")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ProfileRequest(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID")
    target_username: str = Field(..., description="Target username")
    requested_at: int = Field(..., description="Requested at")

    class Config:
        from_attributes = True


class Task(BaseModel):
    id: str = Field(..., description="Task ID")
    telegram_id: str = Field(..., description="Telegram ID")
    status: str = Field(..., description="Status")
    task_details: str = Field(..., description="Task details")
    enqueued_ts: int = Field(..., description="Enqueued timestamp")
    is_premium: int = Field(..., description="Is premium")
    is_bot: int = Field(..., description="Is bot")
    username: str = Field(..., description="Username")
    target_username: str = Field(..., description="Target username")
    description: str = Field(..., description="Description")
    created_at: int = Field(..., description="Created at")
    updated_at: int = Field(..., description="Updated at")

    class Config:
        from_attributes = True


class UserRequestLog(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID")
    requested_at: int = Field(..., description="Requested at")

    class Config:
        from_attributes = True
