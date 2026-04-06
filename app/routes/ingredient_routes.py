from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.business import Business
from ..schemas.ingredient import IngredientPurchaseCreate, IngredientResponse
from ..utils.dependencies import get_current_business_owner
from ..models.user import User
from ..core.database import get_db
from ..services.ingredient_service import IngredientService

router = APIRouter(tags=["Ingredients"])    

@router.get("/", response_model=list[IngredientResponse])
async def list_ingredients(
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(get_current_business_owner),
    search: Optional[str] = Query(None, description="Search ingredients by name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=20, description="Number of items per page (1-20)")
):
    service = IngredientService(db)
    return await service.list_by_business_id(
        business_id=business_owner.id,
        page=page,
        size=size,
        search=search,
    )
@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    ingredient_data: IngredientPurchaseCreate,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = IngredientService(db)
    return await service.create(
        business_id=business.id,
        schema=ingredient_data,
    )
    
@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: int,
    db: AsyncSession = Depends(get_db),
    business: Business = Depends(get_current_business_owner)
):
    service = IngredientService(db)
    return await service.delete(ingredient_id=ingredient_id)