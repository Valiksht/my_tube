"""CRUD операции для пользователей."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.users import User
from app.core.security import hash_password


class UserRepository(BaseRepository[User]):
    """Репозиторий для пользователей."""
    
    async def get_by_username(
        self, 
        db: AsyncSession, 
        username: str,
    ) -> User | None:
        """Получить пользователя по логину."""
        return await self.get_by(db, username=username)
    
    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> User | None:
        """Получить пользователя по email."""
        return await self.get_by(db, email=email)
    
    async def create_user(
        self,
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """Создать нового пользователя с хешированным паролем."""
        hashed = hash_password(password)
        return await self.create(db, {
            "username": username,
            "email": email,
            "hashed_password": hashed,
        })
    
    async def update_user(
        self,
        db: AsyncSession,
        user: User,
        obj_data: dict[str, Any],
    ) -> User:
        """Обновить пользователя.
        
        Если передан пароль — хеширует его.
        """
        if "password" in obj_data:
            obj_data["hashed_password"] = hash_password(obj_data.pop("password"))
        return await self.update(db, user, obj_data)
    
    async def get_all_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Получить список всех пользователей."""
        return await self.get_all(db, skip=skip, limit=limit)


user_repo = UserRepository(User)
