from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.ingredients import IngredientPriceHistory, Ingredient
from ..utils.escape_like_param import escape_like_param

class IngredientPriceHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, history_id: int) -> Optional[IngredientPriceHistory]:
        result = await self.db.execute(select(IngredientPriceHistory).options(
            joinedload(IngredientPriceHistory.ingredient)
                .joinedload(Ingredient.base_unit),
            joinedload(IngredientPriceHistory.purchase_unit),
        ).where(IngredientPriceHistory.id == history_id))
        return result.scalar_one_or_none()
    
    async def list_by_business(
        self,
        business_id: int,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[IngredientPriceHistory]:
        query = select(IngredientPriceHistory).options(
            joinedload(IngredientPriceHistory.ingredient)
                .joinedload(Ingredient.base_unit),
            joinedload(IngredientPriceHistory.purchase_unit),
        ).where(
            IngredientPriceHistory.business_id == business_id
        )
        
        if search:
            safe_search = escape_like_param(search)
            query = query.where(
                IngredientPriceHistory.ingredient.has(
                    Ingredient.name.ilike(f"%{safe_search}%")
                )
            )
        query = query.order_by(IngredientPriceHistory.created_at.desc()) \
                     .limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_ingredient_id(self, ingredient_id: int) -> List[IngredientPriceHistory]:
        result = await self.db.execute(select(IngredientPriceHistory).options(
            joinedload(IngredientPriceHistory.ingredient)
                .joinedload(Ingredient.base_unit),
            joinedload(IngredientPriceHistory.purchase_unit),
        ).where(IngredientPriceHistory.ingredient_id == ingredient_id))
        return result.scalars().all()

    async def get_latest_by_ingredient_id(self, ingredient_id: int) -> Optional[IngredientPriceHistory]:
        result = await self.db.execute(select(IngredientPriceHistory).options(
            joinedload(IngredientPriceHistory.purchase_unit),
        ).where(IngredientPriceHistory.ingredient_id == ingredient_id).order_by(
            IngredientPriceHistory.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, history_data: dict) -> IngredientPriceHistory:
        new_history = IngredientPriceHistory(**history_data)
        self.db.add(new_history)
        await self.db.flush()
        return new_history
