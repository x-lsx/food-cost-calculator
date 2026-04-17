from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional

from .unit import UnitResponse

## Ingredient ##

class IngredientCreate(BaseModel):
    name: str = Field(..., description="Название ингредиента.")
    base_unit_id: int = Field(..., description="ID базовой единицы измерения для ингредиента.")

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название ингредиента.")
    current_price: Optional[Decimal] = Field(None, description="Стоимость ингредиента за базовую единицу измерения.")
    
class IngredientResponse(BaseModel):
    id: int = Field(..., description="ID ингредиента.")
    name: str = Field(..., description="Название ингредиента.")
    slug: str = Field(..., description="Уникальный слаг для ингредиента.")
    current_price: Decimal = Field(..., description="Стоимость ингредиента за базовую единицу измерения.")
    base_unit: UnitResponse = Field(..., description="Название базовой единицы измерения для ингредиента.")
    created_at: datetime = Field(..., description="Дата создания ингредиента.")
    updated_at: datetime = Field(..., description="Дата последнего обновления ингредиента.")
    
    model_config = ConfigDict(from_attributes=True)

class IngredientInResponse(BaseModel):
    id: int = Field(..., description="ID ингредиента.")
    name: str = Field(..., description="Название ингредиента.")
    base_unit: UnitResponse = Field(..., description="Единица измерения ингредиента.")
    current_price: Decimal = Field(..., description="Стоимость ингредиента за базовую единицу измерения.")
    created_at: datetime = Field(..., description="Дата создания ингредиента.")
    updated_at: datetime = Field(..., description="Дата последнего обновления ингредиента.")

    model_config = ConfigDict(from_attributes=True)
    
## IngredientPriceHistory ##

class IngredientPriceHistoryResponse(BaseModel):
    id: int = Field(..., description="ID закупки ингредиента.")
    ingredient: IngredientInResponse = Field(..., description="Ингредиент.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.")
    purchase_unit: UnitResponse = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.")
    created_at: datetime = Field(..., description="Дата создания закупки.")
    updated_at: datetime = Field(..., description="Дата последнего обновления закупки.")

    model_config = ConfigDict(from_attributes=True)


class IngredientPurchaseCreate(BaseModel):
    name: str = Field(..., description="Название ингредиента.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.", gt=0)
    purchase_unit_id: int = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.", gt=0)
    base_unit_id: int = Field(..., description="Базовая единаца измерения")
    
class IngredientPriceHistoryCreate(BaseModel):
    ingredient_id: int = Field(..., description="ID ингредиента.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.", gt=0)
    purchase_unit_id: int = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.", gt=0)
    
    @model_validator(mode='after')
    def validate_price(self):
        if self.purchase_price is not None and self.purchase_price <= 0:
            raise ValueError('Purchase price must be > 0 if provided')
        return self
    
    @model_validator(mode='after')
    def validate_quantity(self):
        if self.purchase_quantity is not None and self.purchase_quantity <= 0:
            raise ValueError('Purchase quantity must be > 0 if provided')
        return self

class IngredientPriceHistoryCreateResponse(BaseModel):
    id: int = Field(..., description="ID закупки ингредиента.")
    ingredient_id: int = Field(..., description="ID ингредиента.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.", gt=0)
    purchase_unit_id: int = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.", gt=0)
    created_at: datetime = Field(..., description="Дата создания закупки.")
    updated_at: datetime = Field(..., description="Дата последнего обновления закупки.")

    model_config = ConfigDict(from_attributes=True)
    
