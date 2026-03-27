from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.flush()
        return new_user
    
    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.flush()
        return user
