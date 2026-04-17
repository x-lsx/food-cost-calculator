from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional


from ..repositories.unit import UnitRepository
from ..schemas.unit import UnitCreate, UnitResponse, UnitUpdate


class UnitService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UnitRepository(db)
    
    async def get_by_id(self, unit_id: int) -> UnitResponse:
        unit = await self.repo.get_by_id(unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found."
            )
        return UnitResponse.model_validate(unit)
    
    async def list_not_base_units(self) -> List[UnitResponse]:
        units = await self.repo.get_not_base_units()
        return [UnitResponse.model_validate(unit) for unit in units]
    
    async def list_base_units(self) -> List[UnitResponse]:
        units = await self.repo.get_base_units()
        return [UnitResponse.model_validate(unit) for unit in units]