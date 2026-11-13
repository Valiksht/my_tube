"""CRUD операции для видео."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.video import Video
from app.models.enum import VideoPrivacy


class VideoRepository(BaseRepository[Video]):
    """Репозиторий для видео."""
    
    async def get_by_channel(
        self,
        db: AsyncSession,
        channel_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Получить видео канала."""
        query = (
            select(self.model)
            .where(
                self.model.channel_id == channel_id,
                self.model.privacy == VideoPrivacy.PUBLIC.value,
                self.model.is_published == True,  # noqa: E712
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_public_videos(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Получить список публичных видео."""
        return await self.get_all(
            db,
            skip=skip,
            limit=limit,
            privacy=VideoPrivacy.PUBLIC.value,
            is_published=True,
        )
    
    async def search_videos(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Поиск видео по названию."""
        sql_query = (
            select(self.model)
            .where(
                self.model.privacy == VideoPrivacy.PUBLIC.value,
                self.model.is_published == True,  # noqa: E712
                self.model.title.ilike(f"%{query}%"),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(sql_query)
        return result.scalars().all()
    
    async def create_video(
        self,
        db: AsyncSession,
        channel_id: int,
        title: str,
        description: str = "",
        privacy: str = "public",
    ) -> Video:
        """Создать новое видео."""
        return await self.create(db, {
            "channel_id": channel_id,
            "title": title,
            "description": description,
            "privacy": privacy,
        })
    
    async def increment_view_count(
        self,
        db: AsyncSession,
        video: Video,
    ) -> Video:
        """Увеличить счётчик просмотров."""
        video.view_count += 1
        await db.flush()
        return video


video_repo = VideoRepository(Video)
