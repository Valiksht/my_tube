"""Pydantic схемы для комментариев."""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CommentBase(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    video_id: int
    user_id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
