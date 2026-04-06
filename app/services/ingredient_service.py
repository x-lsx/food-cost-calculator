from decimal import Decimal
from fastapi import status, HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..repositories.ingredient import IngredientRepository
from ..repositories.unit import UnitRepository
from ..repositories.ingredient_price_history import IngredientPriceHistoryRepository
from ..schemas.ingredient import IngredientPurchaseCreate, IngredientResponse, IngredientResponse


class IngredientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IngredientRepository(db)
        self.unit_repo = UnitRepository(db)
        self.history_repo = IngredientPriceHistoryRepository(db)

    async def _generate_slug(
        self,
        name: str,
    ) -> str:
        base_slug = slugify(name)
        slug = base_slug
        index = 1
        while await self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{index}"
            index += 1
        return slug

    async def get_ingredient_by_id(
        self,
        ingredient_id: int,
        business_id: int,
    ) -> IngredientResponse:
        ingredient = await self.repo.get_by_id(ingredient_id)
        if not ingredient or ingredient.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The ingredient was not found or you do not have access.")
        return IngredientResponse.model_validate(ingredient)

    async def list_by_business_id(
        self,
        business_id: int,
        page: int,
        size: int,
        search: Optional[str] = None,
    ) -> List[IngredientResponse]:

        if page < 1:
            page = 1
        if size < 1 or size > 20:
            size = 10

        offset = (page - 1) * size
        ingredients = await self.repo.list_by_business(
            business_id=business_id,
            limit=size,
            offset=offset,
            search=search,
        )
        return [IngredientResponse.model_validate(ing) for ing in ingredients]

    async def _calculate_current_price(
        self,
        purchase_unit_id: int,
        purchase_quantity: Decimal, 
        purchase_price: Decimal, 
    ) -> Decimal:
        if purchase_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purchase quantity must be greater than zero"
            )
        purchase_unit = await self.unit_repo.get_by_id(purchase_unit_id)
        if not purchase_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid purchase unit."
            )
        qty_in_base = purchase_quantity * purchase_unit.conversion_factor_to_base
        current_price = purchase_price / qty_in_base
        
        return current_price
        
    async def create(
        self,
        business_id: int,
        schema: IngredientPurchaseCreate,
    ) -> IngredientResponse:
        
        if await self.repo.name_exists(business_id=business_id, name=schema.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A Ingredient with that name - '{schema.name}' is already exists."
            )
            
        slug = await self._generate_slug(schema.name)

        current_price = await self._calculate_current_price(
            purchase_unit_id=schema.purchase_unit_id,
            purchase_quantity=schema.purchase_quantity,
            purchase_price=schema.purchase_price
        )
        ingredient_data = {
            "name": schema.name,
            "slug": slug,
            "base_unit_id": schema.base_unit_id,
            "current_price": current_price,
            "business_id": business_id,
        }

        new_ingredient = await self.repo.create(ingredient_data)

        history_data = {
            "ingredient_id": new_ingredient.id,
            "business_id": business_id,
            "purchase_quantity": schema.purchase_quantity,
            "purchase_unit_id": schema.purchase_unit_id,
            "purchase_price": schema.purchase_price,
            "supplier_name": schema.supplier_name,
        }
        await self.history_repo.create(history_data)
        
        ingredient_response = await self.repo.get_by_id(new_ingredient.id)
    
        return IngredientResponse.model_validate(ingredient_response)
    
    async def delete(
        self,
        ingredient_id: int,
    ) -> None:
        deleted = await self.repo.delete(ingredient_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        