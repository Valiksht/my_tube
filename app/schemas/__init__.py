"""Pydantic схемы для валидации данных и формирования ответов."""

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.schemas.video import VideoCreate, VideoUpdate, VideoResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.like import LikeCreate, LikeResponse
from app.schemas.subscription import SubscriptionResponse

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    
    # Channel
    "ChannelCreate",
    "ChannelUpdate",
    "ChannelResponse",
    
    # Video
    "VideoCreate",
    "VideoUpdate",
    "VideoResponse",
    
    # Comment
    "CommentCreate",
    "CommentResponse",
    
    # Like
    "LikeCreate",
    "LikeResponse",
    
    # Subscription
    "SubscriptionResponse",
]
