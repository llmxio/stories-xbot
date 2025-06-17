from datetime import datetime
from typing import List, Optional

from supabase import Client

from .models import Payment, Profile, Story, User


class BaseRepository:
    def __init__(self, client: Client):
        self.client = client


class UserRepository(BaseRepository):
    async def create(self, user: User) -> User:
        """Create a new user."""
        data = user.model_dump()
        result = await self.client.table("users").insert(data).execute()
        return User(**result.data[0])

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.client.table("users").select("*").eq("id", user_id).execute()
        return User(**result.data[0]) if result.data else None

    async def update(self, user: User) -> User:
        """Update user information."""
        data = user.model_dump()
        result = await self.client.table("users").update(data).eq("id", user.id).execute()
        return User(**result.data[0])


class StoryRepository(BaseRepository):
    async def create(self, story: Story) -> Story:
        """Create a new story record."""
        data = story.model_dump()
        result = await self.client.table("stories").insert(data).execute()
        return Story(**result.data[0])

    async def get_by_id(self, story_id: int) -> Optional[Story]:
        """Get story by ID."""
        result = await self.client.table("stories").select("*").eq("id", story_id).execute()
        return Story(**result.data[0]) if result.data else None

    async def get_active_stories(self) -> List[Story]:
        """Get all active stories."""
        result = await self.client.table("stories").select("*").eq("is_viewed", False).execute()
        return [Story(**story) for story in result.data]


class ProfileRepository(BaseRepository):
    async def create(self, profile: Profile) -> Profile:
        """Create a new profile monitoring record."""
        data = profile.model_dump()
        result = await self.client.table("profiles").insert(data).execute()
        return Profile(**result.data[0])

    async def get_by_user_id(self, user_id: int) -> List[Profile]:
        """Get all profiles monitored by a user."""
        result = await self.client.table("profiles").select("*").eq("user_id", user_id).execute()
        return [Profile(**profile) for profile in result.data]

    async def update_last_check(self, profile_id: int) -> Profile:
        """Update the last check time for a profile."""
        data = {"last_check": datetime.utcnow()}
        result = await self.client.table("profiles").update(data).eq("id", profile_id).execute()
        return Profile(**result.data[0])


class PaymentRepository(BaseRepository):
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment record."""
        data = payment.model_dump()
        result = await self.client.table("payments").insert(data).execute()
        return Payment(**result.data[0])

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.client.table("payments").select("*").eq("id", payment_id).execute()
        return Payment(**result.data[0]) if result.data else None

    async def get_by_user_id(self, user_id: int) -> List[Payment]:
        """Get all payments for a user."""
        result = await self.client.table("payments").select("*").eq("user_id", user_id).execute()
        return [Payment(**payment) for payment in result.data]
