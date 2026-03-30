from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.user_service import UserService
from ..schemas.user import UserResponse, UserUpdate
from ..utils.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def read_current_user(current_user=Depends(get_current_user)):
    """Получение данных текущего пользователя"""
    return current_user

@router.patch("/profile", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    return await service.update_user(current_user.id, user_data)
