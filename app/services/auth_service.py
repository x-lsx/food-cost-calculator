from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException

from ..schemas.user import UserCreate,  UserLogin
from ..repositories.user import UserRepository
from ..utils.security import hashed_password, verify_password
from ..utils.jwt_manager import create_access_token, create_refresh_token

import logging

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.logger = logging.getLogger(__name__)

    async def register_user(self, user_data: UserCreate) -> dict:
        self.logger.info(f"Attempting to register user with email: {user_data.email}")
        email_exists = await self.user_repository.get_user_by_email(user_data.email)
        if email_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Имя пользователя уже занято")
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password(user_data.password)
        new_user = await self.user_repository.create_user(user_dict)
        self.logger.info(f"User registered successfully with ID: {new_user.id}")
        token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id})
        refresh_token = create_refresh_token(
            data={"sub": new_user.email, "user_id": new_user.id})
        return {"access_token": token, "refresh_token": refresh_token, "token_type": "Bearer"}

    async def login_user(self, user_data: UserLogin) -> dict:
        self.logger.info(f"Attempting to log in user with email: {user_data.email}")
        user = await self.user_repository.get_user_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Неверное имя пользователя или пароль")
        self.logger.info(f"User logged in successfully with ID: {user.email}")
        token = create_access_token(
            data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id})
        return {"access_token": token, "refresh_token": refresh_token, "token_type": "Bearer"}
