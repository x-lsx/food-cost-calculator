from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, HTTPException

from ..models.business import Business
from ..models.user import User
from ..schemas.token import TokenData
from ..repositories.business import BusinessRepository
from ..services.user_service import UserService
from ..utils.jwt_manager import decode_access_token
from ..core.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем токен
        token_data: TokenData = decode_access_token(token)   

    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    # Получаем пользователя из БД
    user = await db.get(User, token_data.user_id)   # если используешь async
    # user = db.query(User).filter(User.id == token_data.user_id).first()  # если sync

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )

    return user

async def get_current_active_superuser(
        current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser required")
    return current_user


async def get_current_business_owner(
    business_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> int:

    business = await BusinessRepository(db).get_business_by_slug(business_slug)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    if business.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the owner of the business",
        )
    return business