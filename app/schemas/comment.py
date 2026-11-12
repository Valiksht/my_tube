"""Pydantic схемы для комментариев."""

from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """Базовая схема комментария."""
    
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    """Схема для создания комментария."""
    
    pass


class CommentResponse(CommentBase):
    """Ответ с данными комментария."""
    
    id: int
    video_id: int
    user_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
