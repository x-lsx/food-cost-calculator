from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from ..schemas.ingredient import IngredientPriceHistoryCreateResponse, IngredientPriceHistoryResponse, IngredientPriceHistoryCreate
from ..repositories.ingredient_price_history import IngredientPriceHistoryRepository
from ..models.ingredients import Ingredient

import logging

class IngredientPriceHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IngredientPriceHistoryRepository(db)
        self.logger = logging.getLogger(__name__)
        
    async def get_history_by_id(
        self,
        history_id: int,
    ) -> Optional[IngredientPriceHistoryResponse]:
        history = await self.repo.get_by_id(history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient price history not found")
        return history
    
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
            limit=page,
            offset=offset,
            search=search,
        )
        return [IngredientPriceHistoryResponse.model_validate(his) for his in histories]
    
    async def get_history_by_ingredient_id(
        self,
        ingredient_id: int,
    ) -> List[IngredientPriceHistoryResponse]:
        histories = await self.repo.get_by_ingredient_id(ingredient_id)
        return histories

    async def create_history(
        self,
        business_id: int,
        schema: IngredientPriceHistoryCreate,
    ) -> IngredientPriceHistoryCreateResponse:
        """Добавление закупки к существующему ингредиенту."""
        self.logger.info(f"Creating price history for ingredient ID {schema.ingredient_id} in business ID {business_id}")
        ingredient = await self.db.get(Ingredient, schema.ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
        create_data = schema.model_dump()
        create_data["business_id"] = business_id
        history = await self.repo.create(create_data)
        self.logger.info(f"Price history created with ID {history.id} for ingredient ID {schema.ingredient_id}")
        return history