from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils.dependencies import user_is_business_owner
from ..core.database import get_db

from ..models.business import Business
from ..schemas.product import ProductCreate, ProductResponse, ProductUpdate
from ..services.product_service import ProductService
from ..routes.product_ingredient_routes import router as product_ingredient_router


router = APIRouter(tags=["Products"])
router.include_router(product_ingredient_router, prefix="/{product_id}/ingredients", tags=["Product Ingredients"])

@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=20, description="Number of items per page (1-20)"),
    search: Optional[str] = Query(None, description="Search products by name"),
):
    service = ProductService(db)
    return await service.list_by_business_slug(
        business_slug=business_owner.slug,
        page=page,
        size=size,
        search=search,
    )
    
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner)
):
    service = ProductService(db)
    return await service.get_by_id(product_id=product_id)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner)
):
    service = ProductService(db)
    return await service.create(
        business_id=business_owner.id,
        schema=product_data,
    )
    
@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner)
):
    service = ProductService(db)
    return await service.update(
        product_id=product_id,
        business_id=business_owner.id,
        schema=product_data,
    )