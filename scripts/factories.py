"""Фабрики для создания тестовых объектов.

Содержит функции create_users, create_channels, create_videos,
create_comments, create_likes, create_subscriptions.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.comment import Comment
from app.models.like import Like
from app.models.subscription import Subscription
from app.models.users import User
from app.models.video import Video
from app.core.security import hash_password
from .test_data import (
    TEST_COMMENTS,
    TEST_CHANNELS,
    TEST_LIKES,
    TEST_SUBSCRIPTIONS,
    TEST_USERS,
    TEST_VIDEOS,
)


async def create_users(
    session: AsyncSession,
) -> dict[str, User]:
    """Создать пользователей и вернуть словарь username -> User."""
    users_by_username: dict[str, User] = {}

    for user_data in TEST_USERS:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            role=user_data["role"],
            is_active=True,
        )

        session.add(user)
        users_by_username[user.username] = user

    await session.flush()

    return users_by_username


async def create_channels(
    session: AsyncSession,
    users_by_username: dict[str, User],
) -> dict[str, Channel]:
    """Создать каналы и вернуть словарь username владельца -> Channel."""
    channels_by_owner_username: dict[str, Channel] = {}

    for channel_data in TEST_CHANNELS:
        owner_username = channel_data["owner_username"]

        channel = Channel(
            user=users_by_username[owner_username],
            name=channel_data["name"],
            description=channel_data["description"],
        )

        session.add(channel)
        channels_by_owner_username[owner_username] = channel

    await session.flush()

    return channels_by_owner_username


async def create_videos(
    session: AsyncSession,
    channels_by_owner_username: dict[str, Channel],
) -> dict[str, Video]:
    """Создать видео и вернуть словарь title -> Video."""
    videos_by_title: dict[str, Video] = {}

    for video_data in TEST_VIDEOS:
        owner_username = video_data["owner_username"]

        video = Video(
            channel=channels_by_owner_username[owner_username],
            title=video_data["title"],
            description=video_data["description"],
            privacy=video_data["privacy"],
            duration=video_data["duration"],
            view_count=video_data["view_count"],
            is_published=video_data["is_published"],
        )

        session.add(video)
        videos_by_title[video.title] = video

    await session.flush()

    return videos_by_title


async def create_comments(
    session: AsyncSession,
    users_by_username: dict[str, User],
    videos_by_title: dict[str, Video],
) -> None:
    """Создать тестовые комментарии."""
    for comment_data in TEST_COMMENTS:
        comment = Comment(
            video=videos_by_title[comment_data["video_title"]],
            user=users_by_username[comment_data["author_username"]],
            content=comment_data["content"],
        )

        session.add(comment)

    await session.flush()


async def create_likes(
    session: AsyncSession,
    users_by_username: dict[str, User],
    videos_by_title: dict[str, Video],
) -> None:
    """Создать тестовые лайки."""
    for like_data in TEST_LIKES:
        like = Like(
            video=videos_by_title[like_data["video_title"]],
            user=users_by_username[like_data["username"]],
        )

        session.add(like)

    await session.flush()


async def create_subscriptions(
    session: AsyncSession,
    users_by_username: dict[str, User],
    channels_by_owner_username: dict[str, Channel],
) -> None:
    """Создать тестовые подписки."""
    for subscription_data in TEST_SUBSCRIPTIONS:
        subscription = Subscription(
            subscribed_user=users_by_username[
                subscription_data["subscriber_username"]
            ],
            subscribed_channel=channels_by_owner_username[
                subscription_data["channel_owner_username"]
            ],
        )

        session.add(subscription)

    await session.flush()
