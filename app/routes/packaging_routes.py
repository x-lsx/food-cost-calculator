from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.business import Business
from ..schemas.packaging import PackagingCreate, PackagingResponse, PackagingUpdate
from ..models.packaging import Packaging

from ..utils.dependencies import get_current_user, get_current_business_owner
from ..core.database import get_db
from ..services.packaging_service import PackagingService


router = APIRouter(tags=["Packaging"])

@router.get("/", response_model=list[PackagingResponse])
async def list_packaging(
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner),
    search: Optional[str] = Query(None, description="Search packaging by name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=20, description="Number of items per page (1-20)")
):
    service = PackagingService(db)
    return await service.list_by_business_id(
        business_id=business.id,
        page=page,
        size=size,
        search=search,
    )

@router.get("/{packaging_id}", response_model=PackagingResponse)
async def get_packaging(
    packaging_id: int,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = PackagingService(db)
    return await service.get_by_id(
        business_id=business.id,
        packaging_id=packaging_id,
    )

@router.post("/", response_model=PackagingResponse, status_code=status.HTTP_201_CREATED)
async def create_packaging(
    packaging_data: PackagingCreate,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = PackagingService(db)
    return await service.create(
        business_id=business.id,
        schema=packaging_data,
    )
    
@router.put("/{packaging_id}", response_model=PackagingResponse)
async def update_packaging(
    packaging_id: int,
    packaging_data: PackagingUpdate,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = PackagingService(db)
    return await service.update(
        business_id=business.id,
        packaging_id=packaging_id,
        schema=packaging_data,
    )

@router.delete("/{packaging_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packaging(
    packaging_id: int,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = PackagingService(db)
    await service.delete(
        packaging_id=packaging_id,
    )