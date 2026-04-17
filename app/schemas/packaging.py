from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

## Packaging ##

class PackagingBase(BaseModel):
    name: str = Field(..., description="Название упаковки.")
    current_price: Decimal = Field(..., description="Актуальная цена упаковки.", gt=0)


class PackagingCreate(PackagingBase):
    pass


class PackagingUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название упаковки.")
    current_price: Optional[Decimal] = Field(None, description="Актуальная цена упаковки.", gt=0)
    
class PackagingResponse(BaseModel):
    id: int = Field(..., description="ID упаковки.")
    name: str = Field(..., description="Название упаковки.")
    current_price: Decimal = Field(..., description="Актуальная цена упаковки.")
    created_at: datetime = Field(..., description="Дата создания упаковки.")
    updated_at: datetime = Field(..., description="Дата последнего обновления упаковки.")

    model_config = ConfigDict(from_attributes=True)
    
## ProductPackaging ##

class ProductPackagingCreate(BaseModel):
    packaging_id: int = Field(..., description="ID упаковки.")
    
class ProductPackagingUpdate(BaseModel):
    packaging_id: Optional[int] = Field(None, description="ID упаковки.")
    
class ProductPackagingResponse(BaseModel):
    id: int = Field(..., description="ID упаковки продукта.")
    packaging: PackagingResponse = Field(..., description="Упаковка.")
    created_at: datetime = Field(..., description="Дата создания упаковки продукта.")
    updated_at: datetime = Field(..., description="Дата последнего обновления упаковки продукта.")

    model_config = ConfigDict(from_attributes=True)

    
    