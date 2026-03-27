from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.unit import Unit


class UnitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        unit_id: int,
    ) -> Optional[Unit]:
        result = await self.db.execute(select(Unit).where(Unit.id == unit_id))
        return result.scalar_one_or_none()
    
    async def get_base_units(self) -> List[Unit]:
        result = await self.db.execute(
            select(Unit).where(Unit.is_base == True)
        )
        return result.scalars().all()
    
    async def create_unit(
        self,
        unit_data: dict,
    ) -> Unit:
        new_unit = Unit(**unit_data)
        self.db.add(new_unit)
        await self.db.flush()
        return new_unit
    
    async def update_unit(
        self,
        unit_id: int,
        update_data: dict,
    ) -> Optional[Unit]:
        unit = await self.get_by_id(unit_id)
        if not unit:
            return None
        for key, value in update_data.items():
            setattr(unit, key, value)
        await self.db.flush()
        return unit