from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import ProductPackagings


class ProductPackagingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        product_packaging_id: int,
    ) -> Optional[ProductPackagings]:
        return await self.db.get(ProductPackagings, product_packaging_id)

    async def get_by_product_id(
        self,
        product_id: int,
    ) -> List[ProductPackagings]:
        query = (
            select(ProductPackagings)
            .where(ProductPackagings.product_id == product_id)
            .options(joinedload(ProductPackagings.packaging))
        )

        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def create(
        self,
        product_id: int,
        packaging_id: int,
    ) -> ProductPackagings:
        new_packaging = ProductPackagings(
            product_id=product_id,
            packaging_id=packaging_id,
        )
        self.db.add(new_packaging)
        await self.db.flush()
        query = (
            select(ProductPackagings)
            .where(ProductPackagings.id == new_packaging.id)
            .options(joinedload(ProductPackagings.packaging))
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, product_packaging_id: int, packaging_id: int) -> Optional[ProductPackagings]:
        packaging = await self.get_by_id(product_packaging_id)
        if not packaging:
            return None

        packaging.packaging_id = packaging_id
        await self.db.flush()
        query = (
            select(ProductPackagings)
            .where(ProductPackagings.id == packaging.id)
            .options(joinedload(ProductPackagings.packaging))
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def delete(self, product_packaging_id: int) -> bool:
        packaging = await self.get_by_id(product_packaging_id)
        if not packaging:
            return False

        await self.db.delete(packaging)
        return True
