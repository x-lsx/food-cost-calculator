from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.business import Business


class BusinessRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_business_by_name(
        self,
        user_id: int,
        search: Optional[str] = None,
    ) -> list[Business]:
        
        query = select(Business).where(Business.owner_id == user_id)
        if search:
            query = query.where(Business.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_business_by_id(self, business_id: int) -> Optional[Business]:
        result = await self.db.execute(select(Business).where(Business.id == business_id))
        return result.scalar_one_or_none()

    async def get_businesses_by_owner_id(self, owner_id: int) -> list[Business]:
        result = await self.db.execute(select(Business).where(Business.owner_id == owner_id))
        return result.scalars().all()

    async def get_business_by_id_and_owner_id(self, business_id: int, owner_id: int) -> Optional[Business]:
        result = await self.db.execute(
            select(Business).where(
                Business.id == business_id,
                Business.owner_id == owner_id
            )
        )
        return result.scalar_one_or_none()

    async def get_business_by_name_and_owner_id(self, name: str, owner_id: int) -> Optional[Business]:
        result = await self.db.execute(
            select(Business).where(
                Business.name == name,
                Business.owner_id == owner_id
            )
        )
        return result.scalars().first()

    async def get_business_by_slug(self, slug: str) -> Optional[Business]:
        result = await self.db.execute(select(Business).where(Business.slug == slug))
        return result.scalars().first()
    
    async def get_business_by_slug_and_owner_id(self, slug: str, owner_id: int) -> Optional[Business]:
        result = await self.db.execute(
            select(Business).where(
                Business.slug == slug,
                Business.owner_id == owner_id
            )
        )
        return result.scalars().first()

    async def create_business(self, business_data: dict) -> Business:
        new_business = Business(**business_data)
        self.db.add(new_business)
        await self.db.flush()
        return new_business

    async def update_business(self, business_id: int, update_data: dict) -> Optional[Business]:
        business = await self.get_business_by_id(business_id)
        if not business:
            return None
        for key, value in update_data.items():
            setattr(business, key, value)
        await self.db.flush()
        return business
