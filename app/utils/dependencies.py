from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, HTTPException

from ..models.business import Business
from ..models.user import User
from ..schemas.token import TokenData
from ..repositories.business_repository import BusinessRepository
from ..services.user_service import UserService
from ..utils.jwt_manager import decode_access_token
from ..core.database import get_db


async def get_current_user(token_data: TokenData = Depends(decode_access_token), db: AsyncSession = Depends(get_db)) -> User:
    user = await UserService(db).get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не активен")
    return user


async def get_current_active_superuser(
        current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser required")
    return current_user


async def get_current_business_owner(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> int:
    result = await BusinessRepository(db).get_business_by_id_and_owner_id(business_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа к этому бизнесу или бизнес не существует"
        )
    return business_id