from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from ..repositories.product_packagings import ProductPackagingsRepository
from ..schemas.packaging import ProductPackagingResponse, ProductPackagingCreate, ProductPackagingUpdate
from ..models.product import ProductPackagings
from ..repositories.product import ProductRepository

class ProductPackagingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductPackagingsRepository(db)
        self.product_repository = ProductRepository(db)
        
    async def get_by_id(self, product_packaging_id: int) -> ProductPackagingResponse:
        result = await self.repo.get_by_id(product_packaging_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product packaging not found."
            )
        return ProductPackagingResponse.model_validate(result)    
        
    async def get_by_product_id(
        self,
        product_id: int,
    ) -> List[ProductPackagingResponse]:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found."
            )
        packagings = await self.repo.get_by_product_id(product_id)
       
        return [ProductPackagingResponse.model_validate(p) for p in packagings]

    async def create(
        self,
        product_id: int,
        packaging_data: ProductPackagingCreate
    ) -> ProductPackagingResponse:
        result = await self.repo.create(product_id, packaging_data.packaging_id)
        return ProductPackagingResponse.model_validate(result)

    async def update(
        self,
        product_packaging_id: int,
        packaging_id: int,
    ) -> ProductPackagingResponse:
        result = await self.repo.update(product_packaging_id, packaging_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product packaging not found."
            )
        return ProductPackagingResponse.model_validate(result)
    
    async def delete(
        self,
        product_packaging_id: int,
    ) -> None:
        success = await self.repo.delete(product_packaging_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product packaging not found."
            )