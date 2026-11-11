"""Pydantic схемы для видео."""

from datetime import datetime

from pydantic import BaseModel, Field


class VideoBase(BaseModel):
    """Базовая схема видео."""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=10000)
    privacy: str = Field(default="public", description="Тип приватности: public, unlisted, private")


class VideoCreate(VideoBase):
    """Схема для создания видео."""
    
    channel_id: int = Field(..., description="ID канала владельца")


class VideoUpdate(BaseModel):
    """Схема для обновления видео."""
    
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10000)
    privacy: str | None = Field(None, description="Тип приватности")
    is_published: bool | None = None


class VideoResponse(VideoBase):
    """Ответ с данными видео."""
    
    id: int
    channel_id: int
    video_url: str | None
    video_object_name: str | None
    thumbnail_url: str | None
    thumbnail_object_name: str | None
    duration: int
    view_count: int
    is_published: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
