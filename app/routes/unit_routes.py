from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.unit import UnitCreate, UnitResponse, UnitUpdate
from ..core.database import get_db
from ..services.unit_service import UnitService


router = APIRouter(prefix="/api/v1", tags=["Units"])

@router.get("/baseunits", response_model=list[UnitResponse])
async def list_base_units(
    db: AsyncSession = Depends(get_db),
):
    service = UnitService(db)
    return await service.list_base_units()

@router.get("/notbaseunits", response_model=list[UnitResponse])
async def list_not_base_units(
    db: AsyncSession = Depends(get_db),
):
    service = UnitService(db)
    return await service.list_not_base_units()

