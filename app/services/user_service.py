from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import  List

from ..schemas.user import  UserUpdate, UserResponse
from ..repositories.user import UserRepository
from ..utils.security import hashed_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        updated_data = user_data.model_dump(exclude_unset=True)

        if "password" in updated_data:
            updated_data["hashed_password"] = hashed_password(
                updated_data.pop("password"))

        updated_user = await self.user_repository.update_user(user_id, updated_data)
        return UserResponse.model_validate(updated_user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return UserResponse.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserResponse:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return UserResponse.model_validate(user)

    async def get_all_users(self) -> List[UserResponse]:
        users = await self.user_repository.get_all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи не найдены")
        return [UserResponse.model_validate(user) for user in users]
