from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import Product, ProductIngredients, ProductPackagings
from ..utils.escape_like_param import escape_like_param


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_by_id(
        self,
        product_id: int,
    ) -> Optional[Product]:
        return await self.db.get(Product, product_id)

    async def get_by_id_with_ingredients(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.ingredients)
                    .selectinload(ProductIngredients.ingredient),
                selectinload(Product.packagings_products)
                    .selectinload(ProductPackagings.packaging),
            )
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug_global(
        self,
        slug: str,
    ) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        business_id: int,
        name: str,
    ) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.business_id == business_id,
                Product.name == name,
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_business_slug(
        self,
        business_slug: str,
        offset: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> List[Product]:
        from ..models.business import Business

        query = select(Product).join(
            Business, Product.business_id == Business.id
        ).where(
            Business.slug == business_slug
        )

        if search:
            safe_search = escape_like_param(search)
            query = query.where(Product.name.ilike(f"%{safe_search}%"))

        query = query.order_by(Product.name.asc()).limit(
            limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        schema: dict,
    ) -> Product:
        product = Product(**schema)
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def update(
        self,
        product_id: int,
        update_data: dict,
    ) -> Product:
        product = await self.get_by_id(product_id)
        
        if not product:
            raise ValueError("Product not found")
        
        for key, value in update_data.items():
            setattr(product, key, value)
        
        await self.db.refresh(product)
        return product