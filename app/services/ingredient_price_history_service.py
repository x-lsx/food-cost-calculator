from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from ..schemas.ingredient import IngredientFullCreate, IngredientResponse, IngredientCardResponse
from ..repositories.ingredient_price_history import IngredientPriceHistoryRepository
from ..models.ingredients import Ingredient

class IngredientPriceHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ingredient_price_history_repository = IngredientPriceHistoryRepository(db)
        
    async def get_history_by_id(
        self,
        history_id: int,
    ) -> Optional[dict]:
        history = await self.ingredient_price_history_repository.get_by_id(history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient price history not found")
        return history
    
    async def list_by_business_id(
        self,
        business_id: int,
        
    ):
        pass
    
    
    async def get_history_by_ingredient_id(
        self,
        ingredient_id: int,
    ) -> List[dict]:
        histories = await self.ingredient_price_history_repository.get_by_ingredient_id(ingredient_id)
        return histories
    
    async def create_history(
        self,
        business_id: int,
        ingredient_data: IngredientFullCreate
    ) -> IngredientResponse:
        
        
        with self.db.begin():
            ingredient = Ingredient(
                name=ingredient_data.name,
                business_id=business_id,
                base_unit_id=ingredient_data.base_unit_id,
                slug=await self._generate_slug(ingredient_data.name)
            )