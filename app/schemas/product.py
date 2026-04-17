from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from .ingredient import IngredientInResponse

## Product ##


class ProductCreate(BaseModel):
    name: str = Field(..., description="Название продукта.")
    sale_price: Decimal = Field(...,
                                description="Цена продажи продукта.", gt=0)
    yield_quantity: Decimal = Field(..., description="Выход продукта.", gt=0)
    yield_unit_id: int = Field(...,
                               description="ID единицы измерения выхода продукта.")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название продукта.")
    sale_price: Optional[Decimal] = Field(
        None, description="Цена продажи продукта.", gt=0)
    yield_quantity: Optional[Decimal] = Field(
        None, description="Выход продукта.", gt=0)
    yield_unit_id: Optional[int] = Field(
        None, description="ID единицы измерения выхода продукта.")


class ProductResponse(BaseModel):
    id: int = Field(..., description="ID продукта.")
    name: str = Field(..., description="Название продукта.")
    slug: str = Field(..., description="Уникальный слаг продукта.")
    sale_price: Decimal = Field(..., description="Цена продажи продукта.")
    cost_price: Decimal = Field(..., description="Себестоимость продукта.")
    yield_quantity: Decimal = Field(..., description="Выход продукта.")
    yield_unit_id: int = Field(...,
                               description="ID единицы измерения выхода продукта.")
    created_at: datetime = Field(...,
                                 description="Дата и время создания продукта.")
    updated_at: datetime = Field(...,
                                 description="Дата и время последнего обновления продукта.")

    model_config = ConfigDict(from_attributes=True)


## ProductIngredients ##


class ProductIngredientCreate(BaseModel):
    ingredient_id: int = Field(..., description="ID ингредиента.")
    quantity: Decimal = Field(
        ..., description="Количество ингредиента, необходимое для приготовления продукта.", gt=0)


class ProductIngredientUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(
        None, description="Количество ингредиента, необходимое для приготовления продукта.", gt=0)


class ProductIngredientResponse(BaseModel):
    id: int = Field(..., description="ID ингредиента в продукте.")
    product_id: int = Field(..., description="ID продукта.")
    ingredient_id: int = Field(..., description="ID ингредиента.")
    quantity: Decimal = Field(
        ..., description="Количество ингредиента, необходимое для приготовления продукта.")
    created_at: datetime = Field(
        ..., description="Дата и время создания связи между продуктом и ингредиентом.")
    updated_at: datetime = Field(
        ..., description="Дата и время последнего обновления связи между продуктом и ингредиентом.")

    model_config = ConfigDict(from_attributes=True)


class ProductIngredientsCardResponse(BaseModel):
    id: int = Field(..., description="ID ингредиента в продукте.")
    ingredient: IngredientInResponse = Field(...,
                                             description="Ингредиент продукта")
    quantity: Decimal = Field(
        ..., description="Количество ингредиента, необходимое для приготовления продукта.")
    created_at: datetime = Field(
        ..., description="Дата и время создания связи между продуктом и ингредиентом.")
    updated_at: datetime = Field(
        ..., description="Дата и время последнего обновления связи между продуктом и ингредиентом.")

    model_config = ConfigDict(from_attributes=True)
