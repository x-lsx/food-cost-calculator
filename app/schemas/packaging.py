from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PackagingBase(BaseModel):
    name: str = Field(..., description="Название упаковки.")
    current_price: Decimal = Field(..., description="Актуальная цена упаковки.")


class PackagingCreate(PackagingBase):
    pass


class PackagingUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название упаковки.")
    current_price: Optional[Decimal] = Field(None,description="Актуальная цена упаковки.")
    
class PackagingResponse(BaseModel):
    id: int = Field(..., description="ID упаковки.")
    name: str = Field(..., description="Название упаковки.")
    current_price: Decimal = Field(..., description="Актуальная цена упаковки.")
    created_at: datetime = Field(..., description="Дата создания упаковки.")
    updated_at: datetime = Field(..., description="Дата последнего обновления упаковки.")

    model_config = ConfigDict(from_attributes=True)
    
    