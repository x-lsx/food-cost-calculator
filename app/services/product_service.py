from decimal import Decimal

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional
import logging 

from ..schemas.product import ProductCreate, ProductResponse, ProductUpdate
from ..repositories.product import ProductRepository


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)
        self.logger = logging.getLogger(__name__)

    async def recalc_product_cost(self, product_id: int) -> None:
        product = await self.repo.get_by_id_with_ingredients(product_id)
        if not product:
            self.logger.warning("Product not found for cost recalculation", extra={"product_id": product_id})
            return
        total_cost = Decimal("0")
        for item in product.ingredients:
            total_cost += item.quantity * item.ingredient.current_price
        for item in product.packagings_products:
            total_cost += item.packaging.current_price
        product.cost_price = total_cost
        await self.db.flush()
        await self.db.commit()
        self.logger.info("Product cost recalculated", extra={"product_id": product_id, "new_cost": str(total_cost)})

    async def _generate_slug(self, name: str) -> str:
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        
        while await self.repo.get_by_slug_global(slug=slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    async def get_by_id(
        self,
        product_id: int,
    ) -> Optional[ProductResponse]:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found."
            )
        return ProductResponse.model_validate(product)

    async def list_by_business_slug(
        self,
        business_slug: str,
        page: int,
        size: int,
        search: Optional[str] = None,
        
    ) -> List[ProductResponse]:
        
        if page < 1:
            page = 1
        if size < 1 or size > 20:
            size = 10
        offset = (page - 1) * size
        products = await self.repo.list_by_business_slug(business_slug, offset, size, search)
        
        return [ProductResponse.model_validate(product) for product in products]
    
    async def create(
        self,
        business_id: int,
        schema: ProductCreate,
    ) -> ProductResponse:
        slug = await self._generate_slug(schema.name)
        create_data = schema.model_dump()
        create_data["business_id"] = business_id
        create_data["slug"] = slug
        create_data["cost_price"] = 0
        new_product = await self.repo.create(create_data)
        return ProductResponse.model_validate(new_product)
    
    
    async def update(
        self,
        product_id: int,
        business_id: int,
        schema: ProductUpdate,
    ) -> ProductResponse:
        existing_product = await self.repo.get_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found."
            )
        if existing_product.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this product."
            )
            
        update_data = schema.model_dump(exclude_unset=True)
        
        if "name" in update_data:
            update_data["slug"] = slugify(update_data["name"])
        
        updated_product = await self.repo.update(product_id, update_data)
        return ProductResponse.model_validate(updated_product)