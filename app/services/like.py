"""Сервисы для работы с лайками.

Бизнес-логика: создание, удаление, проверка лайков.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like
from app.crud.like import like_repo


class LikeService:
    """Сервис для работы с лайками."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def toggle_like(
        self,
        video_id: int,
        user_id: int,
    ) -> Like:
        """Переключить лайк.
        
        Если лайк есть — удаляет. Если нет — создаёт.
        
        Args:
            video_id: ID видео.
            user_id: ID пользователя.
            
        Returns:
            Лайк (созданный или None).
        """
        existing = await like_repo.get_like(
            self.db,
            video_id=video_id,
            user_id=user_id,
        )
        
        if existing:
            await like_repo.remove_like(self.db, existing)
            return existing
        
        return await like_repo.create_like(
            self.db,
            video_id=video_id,
            user_id=user_id,
        )
    
    async def get_like_status(
        self,
        video_id: int,
        user_id: int,
    ) -> bool:
        """Проверить есть ли лайк у пользователя на видео.
        
        Args:
            video_id: ID видео.
            user_id: ID пользователя.
            
        Returns:
            True если пользователь поставил лайк.
        """
        like = await like_repo.get_like(
            self.db,
            video_id=video_id,
            user_id=user_id,
        )
        return like is not None
    
    async def get_video_like_count(
        self,
        video_id: int,
    ) -> int:
        """Получить количество лайков на видео."""
        from sqlalchemy import func, select
        
        query = (
            select(func.count())
            .select_from(Like)
            .where(Like.video_id == video_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

