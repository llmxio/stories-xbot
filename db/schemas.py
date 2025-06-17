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
