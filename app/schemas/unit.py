from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UnitBase(BaseModel):
    name: str = Field(..., description="Название единицы измерения.")
    symbol: str = Field(..., description="Обозначение единицы измерения.")
    type: str = Field(..., description="Тип единицы измерения.")
    is_base: bool = Field(...,
                          description="Является ли единица измерения базовой.")
    conversion_factor_to_base: Decimal = Field(..., description="Коэффицетн для конвертации в базовую ед.измерения.")

    
class UnitCreate(UnitBase):
    pass 

class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название единицы измерения.")
    symbol: Optional[str] = Field(None, description="Обозначение единицы измерения.")
    type: Optional[str] = Field(None, description="Тип единицы измерения.")
    is_base: Optional[bool] = Field(None,
                          description="Является ли единица измерения базовой.")
    conversion_factor_to_base: Optional[Decimal] = Field(None,
                            deprecated = "Коэффицетн для конвертации в базовую ед.измерения.")

class UnitResponse(BaseModel):
    id: int = Field(..., description="ID единицы измерения.")
    name: str = Field(..., description="Название единицы измерения.")
    symbol: str = Field(..., description="Обозначение единицы измерения.")
    type: str = Field(..., description="Тип единицы измерения.")
    is_base: bool = Field(..., description="Является ли единица измерения базовой.")
    conversion_factor_to_base: Decimal = Field(..., description="Коэффицетн для конвертации в базовую ед.измерения.")
    
    model_config = ConfigDict(from_attributes=True)
