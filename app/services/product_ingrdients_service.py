from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional
import logging

from ..repositories.product_ingredients import ProductIngredientsRepository
from ..schemas.product import ProductIngredientResponse, ProductIngredientsCardResponse
from  ..services.product_service import ProductService

class ProductIngredientsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductIngredientsRepository(db)
        self.logger = logging.getLogger(__name__)
        
    async def get_by_id(self, product_ingredient_id: int):
        result = await self.repo.get_by_id(product_ingredient_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ProductIngredient not found."
            )
        return ProductIngredientResponse.model_validate(result)
    
    async def list_by_product_id(
        self,
        product_id: int
    ) -> List[ProductIngredientsCardResponse]:
        result = await self.repo.get_by_product_id(product_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredients for this product not found."
            )
        return [ProductIngredientsCardResponse.model_validate(ing) for ing in result]
    
    async def create(
        self,
        product_id: int,
        ingredient_id: int,
        quantity: Decimal,
    ) -> ProductIngredientResponse:
        result = await self.repo.create(product_id, ingredient_id, quantity)
        
        return ProductIngredientResponse.model_validate(result)

    async def update_quantity(
        self,
        product_ingredient_id: int,
        quantity: Decimal,
    ) -> ProductIngredientsCardResponse:
        result = await self.repo.update_quantity(product_ingredient_id, quantity)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product ingredient not found."
            )
        return ProductIngredientResponse.model_validate(result)
    
    async def delete(self, product_ingredient_id: int) -> None:
        success = await self.repo.delete(product_ingredient_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product ingredient not found."
            )