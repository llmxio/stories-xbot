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
    chat_id: int = Field(..., description="Chat ID")
    username: str = Field(..., description="Username")
    is_bot: bool = Field(..., description="Is bot")
    is_premium: bool = Field(..., description="Is premium")


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class BlockedUser(BaseModel):
    chat_id: int = Field(..., description="Chat ID")
    blocked_at: int = Field(..., description="Blocked at")
    is_bot: int = Field(..., description="Is bot")

    class Config:
        from_attributes = True


class BugReport(BaseModel):
    id: int = Field(..., description="Bug report ID")
    chat_id: int = Field(..., description="Chat ID")
    username: str = Field(..., description="Username")
    description: str = Field(..., description="Description")
    created_at: int = Field(..., description="Created at")

    class Config:
        from_attributes = True


class DownloadQueue(BaseModel):
    id: int = Field(..., description="Download queue ID")
    chat_id: int = Field(..., description="Chat ID")
    target_username: str = Field(..., description="Target username")
    status: str = Field(..., description="Status")
    enqueued_ts: int = Field(..., description="Enqueued timestamp")
    processed_ts: int = Field(..., description="Processed timestamp")
    error: str = Field(..., description="Error")
    task_details: str = Field(..., description="Task details")

    class Config:
        from_attributes = True


class InvalidLinkViolation(BaseModel):
    chat_id: int = Field(..., description="Chat ID")
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
    chat_id: int = Field(..., description="Chat ID")
    target_username: str = Field(..., description="Target username")
    last_checked: int = Field(..., description="Last checked")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ProfileRequest(BaseModel):
    chat_id: int = Field(..., description="Chat ID")
    target_username: str = Field(..., description="Target username")
    requested_at: int = Field(..., description="Requested at")

    class Config:
        from_attributes = True


class Task(BaseModel):
    id: str = Field(..., description="Task ID")
    chat_id: int = Field(..., description="Chat ID")
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
    chat_id: int = Field(..., description="Chat ID")
    requested_at: int = Field(..., description="Requested at")

    class Config:
        from_attributes = True


class Chat(BaseModel):
    id: int = Field(..., description="Chat ID")
    type: str = Field(..., description="Chat type")
    title: Optional[str] = Field(None, description="Chat title")
    username: Optional[str] = Field(None, description="Chat username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    is_forum: bool = Field(default=False, description="Is forum")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
