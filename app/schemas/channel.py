"""Pydantic схемы для каналов."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Базовая схема канала."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название канала",
    )
    description: str = Field(
        "",
        max_length=5000,
        description="Описание канала",
    )


class ChannelCreate(ChannelBase):
    """Схема для создания канала."""
    
    pass


class ChannelUpdate(BaseModel):
    """Схема для обновления канала."""
    
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=5000)
    avatar_url: str | None = Field(None, max_length=500)
    banner_url: str | None = Field(None, max_length=500)


class ChannelResponse(ChannelBase):
    """Ответ с данными канала."""
    
    id: int
    user_id: int
    avatar_url: str | None
    banner_url: str | None
    created_at: datetime
    
    model_config = {"from_attributes": True}
