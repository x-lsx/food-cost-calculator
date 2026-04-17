from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.business import Business
from ..models.user import User
from ..services.business_service import BusinessService
from ..schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate
from ..core.database import get_db
from ..utils.dependencies import get_current_user, user_is_business_owner

from ..routes.ingredient_routes import router as ingredient_router
from ..routes.packaging_routes import router as packaging_router
from ..routes.history_routes import router as history_router
from ..routes.product_routes import router as product_router

router = APIRouter(prefix="/api/v1/businesses", tags=["businesses"])

router.include_router(ingredient_router, prefix="/{business_slug}/ingredients")
router.include_router(packaging_router, prefix="/{business_slug}/packaging")
router.include_router(history_router, prefix="/{business_slug}/history")
router.include_router(product_router, prefix="/{business_slug}/products")


@router.get("/", response_model=list[BusinessResponse])
async def list_businesses(
    db: AsyncSession = Depends(get_db),
    current_user: User=Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search businesses by name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=20, description="Number of items per page (1-20)")
):
    service = BusinessService(db)
    return await service.get_business_by_name(
        user_id=current_user.id,
        page=page,
        size=size,
        search=search,
    )
@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_data: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BusinessService(db)
    return await service.create_business(
        business_data=business_data,
        current_user=current_user
    )

@router.patch("/{business_slug}", response_model=BusinessResponse)
async def update_business(
    business_slug: str,
    update_data: BusinessUpdate,
    business: Business = Depends(user_is_business_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    return await service.update_business(
        business=business,
        update_data=update_data,
    ) 

@router.get("/{business_slug}", response_model=BusinessResponse)
async def get_business(
    business_slug: str,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(user_is_business_owner),
):
    service = BusinessService(db)
    return await service.get_business_by_slug(
        business_slug=business_slug,
    )

