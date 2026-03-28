from pydantic import BaseModel,Field, ConfigDict
from typing import Optional


class BusinessBase(BaseModel):
    name: str = Field(..., description="Навзвание бизнеса.")
    description: Optional[str] = Field(None, description="Описание/доп. инфа.")



class BusinessCreate(BusinessBase):
    pass

class BusinessCreateInternal(BusinessCreate):
    owner_id: int
    slug: str

class BusinessUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Навзвание бизнеса.")
    description: Optional[str] = Field(None, description="Описание/доп. инфа.")
    is_active: Optional[str] = Field(None, description="Активность бизнеса")


class BusinessResponse(BaseModel):
    id: int = Field(..., description="ID бизнеса.")
    name: Optional[str] = Field(None, description="Навзвание бизнеса.")
    slug: Optional[str] = Field(None, description="Уникальный идентификатор бизнеса.")
    description: Optional[str] = Field(None, description="Описание/доп. инфа.")
    is_active: bool = Field(..., description="Активность бизнеса")
    owner_id: int = Field(..., description="ID владельца бизнеса.")
    
    model_config = ConfigDict(from_attributes=True)