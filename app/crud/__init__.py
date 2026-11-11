"""CRUD репозитории для всех сущностей."""

from app.crud.base import BaseRepository
from app.crud.user import user_repo, UserRepository
from app.crud.channel import channel_repo, ChannelRepository
from app.crud.video import video_repo, VideoRepository
from app.crud.comment import comment_repo, CommentRepository
from app.crud.like import like_repo, LikeRepository
from app.crud.subscription import subscription_repo, SubscriptionRepository

__all__ = [
    "BaseRepository",
    
    # User
    "user_repo",
    "UserRepository",
    
    # Channel
    "channel_repo",
    "ChannelRepository",
    
    # Video
    "video_repo",
    "VideoRepository",
    
    # Comment
    "comment_repo",
    "CommentRepository",
    
    # Like
    "like_repo",
    "LikeRepository",
    
    # Subscription
    "subscription_repo",
    "SubscriptionRepository",
]
