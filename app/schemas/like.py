"""Pydantic схемы для лайков."""

from datetime import datetime

from pydantic import BaseModel, Field


class LikeCreate(BaseModel):
    """Схема для создания лайка."""
    
    video_id: int = Field(..., description="ID видео")


class LikeResponse(BaseModel):
    """Ответ с данными лайка."""
    
    id: int
    video_id: int
    user_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
