from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import  UserCreate, UserLogin
from ..schemas.token import TokenResponse



router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# @router.post("/login", response_model=TokenResponse)
# async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)
# ):
#     service = AuthService(db)
#     return await service.login_user(user_data)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    login_data = UserLogin(
        email=form_data.username,
        password=form_data.password
    )

    service = AuthService(db)
    return await service.login_user(login_data)