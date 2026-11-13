"""CRUD операции для комментариев."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import BaseRepository
from app.models.comment import Comment


class CommentRepository(BaseRepository[Comment]):
    """Репозиторий для комментариев."""
    
    async def get_by_video(
        self,
        db: AsyncSession,
        video_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        """Получить комментарии видео."""
        query = (
            select(self.model)
            .where(self.model.video_id == video_id)
            .options(joinedload(Comment.user))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        """Получить комментарии пользователя."""
        return await self.get_all(
            db,
            skip=skip,
            limit=limit,
            user_id=user_id,
        )
    
    async def create_comment(
        self,
        db: AsyncSession,
        video_id: int,
        user_id: int,
        content: str,
    ) -> Comment:
        """Создать комментарий."""
        return await self.create(db, {
            "video_id": video_id,
            "user_id": user_id,
            "content": content,
        })


comment_repo = CommentRepository(Comment)
