"""Сервисы для работы с комментариями.

Бизнес-логика: создание, получение, удаление комментариев.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.crud.comment import comment_repo


class CommentService:
    """Сервис для работы с комментариями."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_comment(
        self,
        video_id: int,
        user_id: int,
        content: str,
    ) -> Comment:
        """Создать комментарий.
        
        Args:
            video_id: ID видео.
            user_id: ID пользователя.
            content: Текст комментария.
            
        Returns:
            Созданный комментарий.
        """
        return await comment_repo.create_comment(
            self.db,
            video_id=video_id,
            user_id=user_id,
            content=content,
        )
    
    async def get_video_comments(
        self,
        video_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        """Получить комментарии видео."""
        return await comment_repo.get_by_video(
            self.db,
            video_id=video_id,
            skip=skip,
            limit=limit,
        )
    
    async def get_user_comments(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        """Получить комментарии пользователя."""
        return await comment_repo.get_by_user(
            self.db,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    
    async def delete_comment(
        self,
        comment: Comment,
        current_user,
        is_moderator=False,
    ) -> None:
        """Удалить комментарий.
        
        Args:
            comment: Комментарий для удаления.
            current_user: Текущий пользователь.
            is_moderator: Флаг модератора.
            
        Raises:
            PermissionError: Если нет прав.
        """
        is_owner = (
            current_user
            and comment.user_id == current_user.id
        )
        
        if not is_owner and not is_moderator:
            raise PermissionError("Not enough permissions")
        
        await comment_repo.remove(self.db, comment)


comment_service = CommentService(None)  # type: ignore[arg-type]
