from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.packaging import Packaging, PackagingProducts


class PackagingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        packaging_id: int,
    ) -> Optional[Packaging]:
        return await self.db.get(Packaging, packaging_id)

    async def get_by_id_for_business(
        self,
        packaging_id: int,
        business_id: int,
    ) -> Optional[Packaging]:
        packaging = await self.db.get(Packaging, packaging_id)
        if packaging and packaging.business_id == business_id:
            return packaging
        return None

    async def name_exists(
        self,
        business_id: int,
        name: str,
    ) -> bool:
        result = await self.db.execute(
            select(Packaging).where(
                Packaging.business_id == business_id,
                Packaging.name == name,
            )
        )
        return result.scalar_one_or_none() is not None
        

    async def list(
        self,
        business_id: int,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Packaging]:

        query = select(Packaging).where(Packaging.business_id == business_id)

        if search:
            query = query.where(Packaging.name.ilike(f"%{search}%"))

        query = query.order_by(Packaging.name.asc()).limit(
            limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, create_data: dict) -> Packaging:
        new_packaging = Packaging(**create_data)
        self.db.add(new_packaging)
        await self.db.flush()
        await self.db.refresh(new_packaging)
        return new_packaging

    async def update(
        self, 
        packaging_id: int, 
        update_data: dict
    ) -> Optional[Packaging]:
        packaging = await self.db.get(Packaging, packaging_id)
        if not packaging:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(packaging, key):
                setattr(packaging, key, value)

        await self.db.flush()
        await self.db.refresh(packaging)
        return packaging

    async def delete(self, business_id: int, packaging_id: int) -> bool:
        packaging = await self.get_by_id_for_business(
            packaging_id, business_id
        )
        if not packaging:
            return False

        await self.db.delete(packaging)
        await self.db.flush()
        return True
