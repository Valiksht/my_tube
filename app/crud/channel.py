"""CRUD операции для каналов."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.channel import Channel


class ChannelRepository(BaseRepository[Channel]):
    """Репозиторий для каналов."""
    
    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Channel | None:
        """Получить канал по ID пользователя."""
        return await self.get_by(db, user_id=user_id)
    
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Channel | None:
        """Получить канал по названию."""
        return await self.get_by(db, name=name)
    
    async def get_channels_with_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Channel]:
        """Получить список каналов."""
        return await self.get_all(db, skip=skip, limit=limit)
    
    async def create_channel(
        self,
        db: AsyncSession,
        user_id: int,
        name: str,
        description: str = "",
    ) -> Channel:
        """Создать новый канал."""
        return await self.create(db, {
            "user_id": user_id,
            "name": name,
            "description": description,
        })


channel_repo = ChannelRepository(Channel)
