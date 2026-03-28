from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

from .unit import UnitResponse
## ========== ##
## Ingredient ##
## ========== ## 
class IngredientCreate(BaseModel):
    name: str = Field(..., description="Название ингредиента.")
    base_unit_id: int = Field(..., description="ID базовой единицы измерения для ингредиента.")

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название ингредиента.")
    current_price: Optional[Decimal] = Field(None, description="Стоимость ингредиента за базовую единицу измерения.")
    
class IngredientCardResponse(BaseModel):
    id: int = Field(..., description="ID ингредиента.")
    name: str = Field(..., description="Название ингредиента.")
    slug: str = Field(..., description="Уникальный слаг для ингредиента.")
    current_price: Decimal = Field(..., description="Стоимость ингредиента за базовую единицу измерения.")
    base_unit: UnitResponse = Field(..., description="Название базовой единицы измерения для ингредиента.")
       
    model_config = ConfigDict(from_attributes=True)

## ====================== ##
## IngredientPriceHistory ##
## ====================== ##             

class IngredientPriceHistoryResponse(BaseModel):
    id: int = Field(..., description="ID закупки ингредиента.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.")
    purchase_unit: UnitResponse = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.")

    model_config = ConfigDict(from_attributes=True)


class IngredientPurchaseCreate(BaseModel):
    '''Для создания Ingredient + IngredientPriceHistory'''
    name: str = Field(..., description="Название ингредиента.")
    supplier_name: str = Field(..., description="Имя поставщика ингредиента.")
    purchase_quantity: Decimal = Field(..., description="Количество закупа.")
    purchase_unit_id: int = Field(..., description="Единица измерения при закупке.")
    purchase_price: Decimal = Field(..., description="Цена закупки.")
    base_unit_id: int = Field(..., description="Базовая единаца измерения")