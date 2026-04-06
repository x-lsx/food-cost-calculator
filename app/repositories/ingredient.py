from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.ingredients import Ingredient


class IngredientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        result = await self.db.execute(select(Ingredient).options(
            joinedload(Ingredient.base_unit)
        ).where(Ingredient.id == ingredient_id))
        return result.scalar_one_or_none()

    async def name_exists(
        self,
        business_id: int,
        name: str,
    ) -> bool:
        result = await self.db.execute(
            select(Ingredient).where(
                Ingredient.business_id == business_id,
                Ingredient.name == name,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_by_slug(self, slug: str) -> Optional[Ingredient]:
        result = await self.db.execute(select(Ingredient).options(
            joinedload(Ingredient.base_unit)
        ).where(Ingredient.slug == slug))
        return result.scalar_one_or_none()

    async def list_by_business(
        self,
        business_id: int,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Ingredient]:
        query = select(Ingredient).options(
            joinedload(Ingredient.base_unit)
        ).where(
            Ingredient.business_id == business_id
        )
        if search:
            query = query.where(Ingredient.name.ilike(f"%{search}%"))
        query = query.order_by(Ingredient.name.asc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, ingredient_data: dict) -> Ingredient:
        new_ingredient = Ingredient(**ingredient_data)
        self.db.add(new_ingredient)
        await self.db.flush()
        await self.db.refresh(new_ingredient)
        return new_ingredient

    async def update(self, ingredient_id: int, update_data: dict) -> Optional[Ingredient]:
        ingredient = await self.get_by_id(ingredient_id)
        if not ingredient:
            return None
        for key, value in update_data.items():
            setattr(ingredient, key, value)
        await self.db.flush()
        await self.db.refresh(ingredient)
        return ingredient

    async def delete(self, ingredient_id: int) -> bool:
        ingredient = await self.db.get(Ingredient, ingredient_id)
        if not ingredient:
            return False
        await self.db.delete(ingredient)
        await self.db.refresh(ingredient)
        return True