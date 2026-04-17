from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..utils.dependencies import user_is_business_owner
from ..models.business import Business
from ..models.ingredients import IngredientPriceHistory
from ..schemas.ingredient import IngredientPriceHistoryCreateResponse, IngredientPriceHistoryResponse, IngredientPriceHistoryCreate
from ..services.ingredient_price_history_service import IngredientPriceHistoryService


router = APIRouter(tags=["IngredientPriceHistory"])

@router.get("/", response_model=list[IngredientPriceHistoryResponse])
async def list(    
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(user_is_business_owner),
    search: Optional[str] = Query(None, description="Search ingredients by name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=20, description="Number of items per page (1-20)")
    ):
    service = IngredientPriceHistoryService(db)
    return await service.list_by_business_id(
        business_id=business.id,
        page=page,
        size=size,
        search=search,
    )
    
@router.post("/", response_model=IngredientPriceHistoryCreateResponse, status_code=status.HTTP_201_CREATED)
async def create(
    history_data: IngredientPriceHistoryCreate,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(user_is_business_owner),
    ):
    service = IngredientPriceHistoryService(db)
    return await service.create_history(
        business_id=business.id,
        schema=history_data,
    )