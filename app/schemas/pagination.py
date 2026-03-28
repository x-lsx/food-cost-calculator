from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы для пагинации")
    size: int = Field(10, ge=1, le=100, description="Количество элементов на странице")
    