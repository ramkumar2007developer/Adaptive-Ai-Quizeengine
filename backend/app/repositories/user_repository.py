"""
User Repository — Data access layer for User entity.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, username: str, email: str, display_name: str, user_id: Optional[str] = None) -> User:
        kwargs = {"username": username, "email": email, "display_name": display_name}
        if user_id:
            kwargs["id"] = user_id
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def ensure_user_exists(self, user_id: str) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            clean_id = user_id.replace("-", "_")[:20]
            user = await self.create(
                user_id=user_id,
                username=f"user_{clean_id}",
                email=f"{clean_id}@quizengine.ai",
                display_name="Adaptive Student"
            )
        return user
