from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import ProductIngredientResponse, ProductIngredientsCardResponse, ProductIngredientCreate, ProductIngredientUpdate
from ..utils.dependencies import user_is_business_owner
from ..core.database import get_db

from ..models.business import Business
from ..services.product_ingrdients_service import ProductIngredientsService
from ..services.product_service import ProductService

router = APIRouter(tags=["Product Ingredients"])


@router.get("/", response_model=list[ProductIngredientsCardResponse])
async def list_product_ingredients(
    product_id: int = Path(..., description="ID of the product"),
    db: AsyncSession = Depends(get_db),
    business_owner: Business = Depends(user_is_business_owner),
):
    service = ProductIngredientsService(db)
    return await service.list_by_product_id(product_id=product_id)


@router.post("/", response_model=ProductIngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_product_ingredient(
    product_id: int = Path(..., description="ID of the product"),
    data: ProductIngredientCreate = Body(...),
    business_owner: Business = Depends(user_is_business_owner),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    service = ProductIngredientsService(db)
    product_service = ProductService(db)
    result = await service.create(
        product_id=product_id,
        ingredient_id=data.ingredient_id,
        quantity=data.quantity,
    )
    background_tasks.add_task(product_service.recalc_product_cost, product_id)
    return result


@router.patch("/{product_ingredient_id}", response_model=ProductIngredientResponse, status_code=status.HTTP_200_OK)
async def update_product_ingredient(
    product_id: int = Path(...),
    prdouct_ingredient_id: int = Path(...),
    data: ProductIngredientUpdate = Body(...),
    business_owner: Business = Depends(user_is_business_owner),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    service = ProductIngredientsService(db)
    product_service = ProductService(db)
    result = await service.update_quantity(
        product_ingredient_id=prdouct_ingredient_id,
        quantity=data.quantity,
    )
    background_tasks.add_task(product_service.recalc_product_cost, product_id)
    return result