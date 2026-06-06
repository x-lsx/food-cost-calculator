from fastapi import APIRouter, Body, Depends, Path, status, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.packaging import (
    ProductPackagingCreate,
    ProductPackagingUpdate,
    ProductPackagingResponse,
)
from ..utils.dependencies import user_is_business_owner
from ..core.database import get_db

from ..models.business import Business
from ..services.product_packagings_service import ProductPackagingsService
from ..services.product_service import ProductService

router = APIRouter(tags=["Product Packagings"])

@router.get("/", response_model=list[ProductPackagingResponse])
async def list_product_packagings(
    product_id: int = Path(..., description="ID of the product"),
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner),
):
    service = ProductPackagingsService(db)
    return await service.get_by_product_id(product_id=product_id)

@router.post("/", response_model=ProductPackagingResponse, status_code=status.HTTP_201_CREATED)
async def create_product_packaging(
    product_id: int = Path(..., description="ID of the product"),
    data: ProductPackagingCreate = Body(...),
    business_owner: Business = Depends(user_is_business_owner),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    service = ProductPackagingsService(db)
    product_service = ProductService(db)
    result = await service.create(
        product_id=product_id,
        packaging_data=data,
    )
    background_tasks.add_task(product_service.recalc_product_cost, product_id)
    return result

@router.patch("/{product_packaging_id}", response_model=ProductPackagingResponse)
async def update_product_packaging(
    product_id: int = Path(..., description="ID of the product"),
    product_packaging_id: int = Path(..., description="ID of the product packaging"),
    data: ProductPackagingUpdate = Body(...),
    business_owner: Business = Depends(user_is_business_owner),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    if data.packaging_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="packaging_id is required")

    service = ProductPackagingsService(db)
    product_service = ProductService(db)
    result = await service.update(
        product_packaging_id=product_packaging_id,
        packaging_id=data.packaging_id,
    )
    background_tasks.add_task(product_service.recalc_product_cost, product_id)
    return result

@router.delete("/{product_packaging_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_packaging(
    product_id: int = Path(..., description="ID of the product"),
    product_packaging_id: int = Path(..., description="ID of the product packaging"),
    business_owner: Business = Depends(user_is_business_owner),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    service = ProductPackagingsService(db)
    await service.delete(product_packaging_id=product_packaging_id)
    product_service = ProductService(db)
    background_tasks.add_task(product_service.recalc_product_cost, product_id)
