"""SQLAlchemy модели YouTube Clone.

Экспорт всех моделей и типов для использования в приложении.
Используется только в базовом импорте: from app.models import *
"""

# Базовая модель и сессия
from app.models.base import Base, AsyncSessionLocal, get_async_session

# Модели SQLAlchemy
from app.models.users import User
from app.models.channel import Channel
from app.models.video import Video, VideoPrivacy
from app.models.like import Like
from app.models.comment import Comment
from app.models.subscription import Subscription

# Python Enum (не нативные типы PostgreSQL)
from app.models.enum import UserRole, CommentStatus, VideoStatus, LikeStatus


__all__ = [
    # Базовая модель и сессия
    "Base",
    "AsyncSessionLocal",
    "get_async_session",
    
    # Модели
    "User",
    "Channel", 
    "Video",
    "VideoPrivacy",
    "Like",
    "Comment",
    "Subscription",
    
    # Enum (Python, не DB типы)
    "UserRole",
    "CommentStatus",
    "VideoStatus",
    "LikeStatus"
]