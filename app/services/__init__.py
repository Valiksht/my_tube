"""Сервисы бизнес-логики приложения."""

from app.services.auth import auth_service, AuthService
from app.services.video import video_service, VideoService
from app.services.comment import comment_service, CommentService
from app.services.like import like_service, LikeService
from app.services.subscription import subscription_service, SubscriptionService
from app.services.moderation import moderation_service, ModerationService
from app.services.video_processing import video_processor, VideoProcessor

__all__ = [
    # Auth
    "auth_service",
    "AuthService",
    
    # Video
    "video_service",
    "VideoService",
    
    # Comment
    "comment_service",
    "CommentService",
    
    # Like
    "like_service",
    "LikeService",
    
    # Subscription
    "subscription_service",
    "SubscriptionService",
    
    # Moderation
    "moderation_service",
    "ModerationService",
    
    # Video Processing
    "video_processor",
    "VideoProcessor",
]
