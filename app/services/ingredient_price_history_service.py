from decimal import Decimal

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from ..repositories.unit import UnitRepository

from ..schemas.ingredient import IngredientPriceHistoryCreateResponse, IngredientPriceHistoryResponse, IngredientPriceHistoryCreate
from ..repositories.ingredient_price_history import IngredientPriceHistoryRepository
from ..models.ingredients import Ingredient

import logging

class IngredientPriceHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.unit_repo = UnitRepository(db)
        self.repo = IngredientPriceHistoryRepository(db)
        self.logger = logging.getLogger(__name__)
    
    async def _calculate_current_price(
        self,
        purchase_unit_id: int,
        purchase_quantity: Decimal, 
        purchase_price: Decimal, 
    ) -> Decimal:
        if purchase_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purchase quantity must be greater than zero"
            )
        purchase_unit = await self.unit_repo.get_by_id(purchase_unit_id)
        if not purchase_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid purchase unit."
            )
        qty_in_base = purchase_quantity * purchase_unit.conversion_factor_to_base
        current_price = purchase_price / qty_in_base
        
        return current_price
    
    async def get_history_by_id(
        self,
        history_id: int,
    ) -> Optional[IngredientPriceHistoryResponse]:
        history = await self.repo.get_by_id(history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient price history not found")
        return IngredientPriceHistoryResponse.model_validate(history)
    
    async def list_by_business_id(
        self,
        business_id: int,
        page: int,
        size: int,
        search: Optional[str] = None,
    ) -> List[IngredientPriceHistoryResponse]:
        
        if page < 1:
            page = 1
        if size < 1 or size > 20:
            size = 10

        offset = (page - 1) * size
        histories = await self.repo.list_by_business(
            business_id=business_id,
            limit=size,
            offset=offset,
            search=search,
        )
        return [IngredientPriceHistoryResponse.model_validate(his) for his in histories]
    
    async def get_history_by_ingredient_id(
        self,
        ingredient_id: int,
    ) -> List[IngredientPriceHistoryResponse]:
        histories = await self.repo.get_by_ingredient_id(ingredient_id)
        return [IngredientPriceHistoryResponse.model_validate(h) for h in histories]

    # async def create_history(
    #     self,
    #     business_id: int,
    #     schema: IngredientPriceHistoryCreate,
    # ) -> IngredientPriceHistoryCreateResponse:
    #     """Добавление закупки к существующему ингредиенту."""
        
    #     self.logger.info(f"Creating price history for ingredient.")
    #     ingredient = await self.db.get(Ingredient, schema.ingredient_id)
    #     if not ingredient:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    #     create_data = schema.model_dump()
    #     create_data["business_id"] = business_id
    #     current_price = await self._calculate_current_price(
    #         schema.purchase_unit_id,
    #         schema.purchase_quantity,
    #         schema.purchase_price,
    #     )
    #     ingredient.current_price = current_price
        
        
    #     history = await self.repo.create(create_data)
    #     self.logger.info("Price history created.")
    #     return history  