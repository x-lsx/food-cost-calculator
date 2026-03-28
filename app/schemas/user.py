from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    
class UserCreate(UserBase):
    password: str = Field(..., description="Пароль пользователя")

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    password: Optional[str] = Field(None, description="Пароль пользователя")
    
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

class UserResponse(UserBase):
    id: int = Field(..., description="ID пользователя")
    is_active: bool = Field(..., description="Активен ли пользователь")
    is_superuser: bool = Field(..., description="Является ли пользователь суперпользователем")
    created_at: datetime = Field(..., description="Дата и время создания пользователя")
    
    model_config = ConfigDict(from_attributes = True)