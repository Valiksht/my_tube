"""CRUD операции для лайков."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.like import Like


class LikeRepository(BaseRepository[Like]):
    """Репозиторий для лайков."""
    
    async def get_like(
        self,
        db: AsyncSession,
        video_id: int,
        user_id: int,
    ) -> Like | None:
        """Получить лайк пользователя на видео."""
        return await self.get_by(
            db,
            video_id=video_id,
            user_id=user_id,
        )
    
    async def create_like(
        self,
        db: AsyncSession,
        video_id: int,
        user_id: int,
    ) -> Like:
        """Создать лайк."""
        return await self.create(db, {
            "video_id": video_id,
            "user_id": user_id,
        })
    
    async def remove_like(
        self,
        db: AsyncSession,
        like: Like,
    ) -> None:
        """Удалить лайк."""
        await self.remove(db, like)


like_repo = LikeRepository(Like)
