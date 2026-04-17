from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import Product, ProductIngredients
from ..models.ingredients import Ingredient


class ProductIngredientsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        product_ingredient_id: int,
    ) -> Optional[ProductIngredients]:
        return await self.db.get(ProductIngredients, product_ingredient_id)

    async def get_by_product_id(
        self,
        product_id: int,
    ) -> List[ProductIngredients]:
        query = (
            select(ProductIngredients)
                .where(ProductIngredients.product_id == product_id)
                .options(
                    selectinload(ProductIngredients.ingredient)
                         .selectinload(Ingredient.base_unit)
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def create(
        self,
        product_id: int,
        ingredient_id: int,
        quantity: Decimal,
    ) -> ProductIngredients:
        product_ingredient = ProductIngredients(
            product_id=product_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
        )
        self.db.add(product_ingredient)
        await self.db.flush()
        return product_ingredient

    async def update_quantity(
        self,
        product_ingredient_id: int,
        quantity: Decimal,
    ) -> Optional[ProductIngredients]:
        product_ingredient = await self.get_by_id(product_ingredient_id)
        if not product_ingredient:
            return None
        product_ingredient.quantity = quantity
        await self.db.flush()
        return product_ingredient

    async def delete(
        self,
        product_ingredient_id: int,
    ) -> bool:
        product_ingredient = await self.get_by_id(product_ingredient_id)
        if not product_ingredient:
            return False
        await self.db.delete(product_ingredient)
        return True

