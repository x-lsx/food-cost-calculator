from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class TokenBase(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default = "Bearer", description="Тип токена")
    
    model_config = ConfigDict(populate_by_name=True)
    
class TokenData(BaseModel):
    email: Optional[str] = Field(None, description="Email пользователя")
    user_id: Optional[int] = Field(None, description="ID пользователя")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str