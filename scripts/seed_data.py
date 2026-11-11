"""Скрипт для заполнения базы данных тестовыми данными.

Создаёт тестовых пользователей, каналы, видео, комментарии, лайки и подписки.
Запускается один раз после применения миграций.

Использование:
    python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Добавляем корень проекта в путь импорта.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.channel import Channel
from app.models.comment import Comment
from app.models.enum import UserRole, VideoPrivacy
from app.models.like import Like
from app.models.subscription import Subscription
from app.models.users import User
from app.models.video import Video


DATABASE_URL = get_settings().database_url


# ---------------------------------------------------------------------------
# Тестовые данные
# ---------------------------------------------------------------------------

TEST_USERS = [
    {
        "username": "admin",
        "email": "admin@mytube.com",
        "password": "admin123",
        "role": UserRole.ADMIN.value,
    },
    {
        "username": "moderator",
        "email": "mod@mytube.com",
        "password": "mod123456",
        "role": UserRole.MODERATOR.value,
    },
    {
        "username": "user1",
        "email": "user1@mytube.com",
        "password": "user123456",
        "role": UserRole.USER.value,
    },
    {
        "username": "user2",
        "email": "user2@mytube.com",
        "password": "user123456",
        "role": UserRole.USER.value,
    },
    {
        "username": "user3",
        "email": "user3@mytube.com",
        "password": "user123456",
        "role": UserRole.USER.value,
    },
]

TEST_CHANNELS = [
    {
        "owner_username": "admin",
        "name": "Admin Channel",
        "description": "Официальный канал администратора",
    },
    {
        "owner_username": "moderator",
        "name": "Moderator Hub",
        "description": "Канал модератора",
    },
    {
        "owner_username": "user1",
        "name": "Tech Reviews",
        "description": "Обзоры технологий и гаджетов",
    },
    {
        "owner_username": "user2",
        "name": "Cooking Master",
        "description": "Кулинарные рецепты и советы",
    },
    {
        "owner_username": "user3",
        "name": "Gaming Zone",
        "description": "Игровые обзоры и стримы",
    },
]

TEST_VIDEOS = [
    {
        "owner_username": "user1",
        "title": "Обзор iPhone 15 Pro Max",
        "description": (
            "Подробный обзор нового флагмана Apple. Рассматриваем камеру, "
            "производительность, батарею и все новые функции."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 845,
        "view_count": 15420,
        "is_published": True,
    },
    {
        "owner_username": "user1",
        "title": "Лучшие смартфоны 2024 года",
        "description": (
            "Топ-10 смартфонов этого года. Сравнение камер, "
            "производительности и цены."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 1230,
        "view_count": 8930,
        "is_published": True,
    },
    {
        "owner_username": "user1",
        "title": "Как выбрать ноутбук в 2024",
        "description": (
            "Гайд по выбору ноутбука: от бюджетных до игровых моделей."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 960,
        "view_count": 5670,
        "is_published": True,
    },
    {
        "owner_username": "user2",
        "title": "Идеальный борщ — классический рецепт",
        "description": (
            "Учимся готовить настоящий борщ по бабушкиному рецепту. "
            "Секреты приготовления."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 720,
        "view_count": 23100,
        "is_published": True,
    },
    {
        "owner_username": "user2",
        "title": "5 рецептов за 15 минут",
        "description": (
            "Быстрые и вкусные рецепты для тех, кто не любит "
            "тратить время на кухне."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 900,
        "view_count": 18750,
        "is_published": True,
    },
    {
        "owner_username": "user2",
        "title": "Домашний хлеб без дрожжей",
        "description": (
            "Простой рецепт вкусного домашнего хлеба "
            "без использования дрожжей."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 540,
        "view_count": 12300,
        "is_published": True,
    },
    {
        "owner_username": "user3",
        "title": "GTA 6 — Первый взгляд",
        "description": (
            "Анализируем первый трейлер GTA 6. Всё что мы знаем о игре."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 680,
        "view_count": 45200,
        "is_published": True,
    },
    {
        "owner_username": "user3",
        "title": "Топ-10 игр 2024 года",
        "description": "Лучшие игры этого года по версии нашего канала.",
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 1500,
        "view_count": 32100,
        "is_published": True,
    },
    {
        "owner_username": "user3",
        "title": "Как собрать ПК для игр",
        "description": (
            "Полное руководство по сборке игрового компьютера: "
            "от выбора комплектующих до настройки."
        ),
        "privacy": VideoPrivacy.PUBLIC.value,
        "duration": 2100,
        "view_count": 28900,
        "is_published": True,
    },
    {
        "owner_username": "user1",
        "title": "Секретный проект",
        "description": "Это приватное видео, видимое только владельцу канала.",
        "privacy": VideoPrivacy.PRIVATE.value,
        "duration": 300,
        "view_count": 0,
        "is_published": False,
    },
]

TEST_COMMENTS = [
    {
        "video_title": "Обзор iPhone 15 Pro Max",
        "author_username": "user2",
        "content": "Отличный обзор! Ждал выхода этого телефона.",
    },
    {
        "video_title": "Обзор iPhone 15 Pro Max",
        "author_username": "user3",
        "content": "Камера просто огонь 🔥",
    },
    {
        "video_title": "Лучшие смартфоны 2024 года",
        "author_username": "user1",
        "content": "Согласен с рейтингом, но Sony была бы выше.",
    },
    {
        "video_title": "Идеальный борщ — классический рецепт",
        "author_username": "user1",
        "content": "Попробовала по рецепту — получилось идеально!",
    },
    {
        "video_title": "Идеальный борщ — классический рецепт",
        "author_username": "user3",
        "content": "Бабушка такой же борщ готовила 😊",
    },
    {
        "video_title": "5 рецептов за 15 минут",
        "author_username": "user2",
        "content": "Рецепт №3 — мой любимый, готовлю каждую неделю.",
    },
    {
        "video_title": "GTA 6 — Первый взгляд",
        "author_username": "user1",
        "content": "Наконец-то дождались! GTA 6 будет топ.",
    },
    {
        "video_title": "GTA 6 — Первый взгляд",
        "author_username": "user2",
        "content": "Графика выглядит невероятно!",
    },
    {
        "video_title": "Топ-10 игр 2024 года",
        "author_username": "user3",
        "content": "Elden Ring заслуживал первого места!",
    },
    {
        "video_title": "Как собрать ПК для игр",
        "author_username": "user1",
        "content": "Собрал ПК по гайду — работает отлично!",
    },
    {
        "video_title": "Обзор iPhone 15 Pro Max",
        "author_username": "user1",
        "content": "Можно ли сравнить с Samsung S24?",
    },
    {
        "video_title": "Домашний хлеб без дрожжей",
        "author_username": "user2",
        "content": "Хлеб получился супер, спасибо за рецепт!",
    },
    {
        "video_title": "Секретный проект",
        "author_username": "user3",
        "content": "Когда релиз GTA 6?",
    },
    {
        "video_title": "Как выбрать ноутбук в 2024",
        "author_username": "user2",
        "content": "Беру MacBook Air M3, рекомендую!",
    },
    {
        "video_title": "Топ-10 игр 2024 года",
        "author_username": "user1",
        "content": "Cyberpunk 2077 — моя игра года!",
    },
]

TEST_LIKES = [
    {"video_title": "Обзор iPhone 15 Pro Max", "username": "user2"},
    {"video_title": "Обзор iPhone 15 Pro Max", "username": "user3"},
    {"video_title": "Обзор iPhone 15 Pro Max", "username": "user1"},
    {"video_title": "Лучшие смартфоны 2024 года", "username": "user1"},
    {"video_title": "Лучшие смартфоны 2024 года", "username": "user3"},
    {"video_title": "Идеальный борщ — классический рецепт", "username": "user1"},
    {"video_title": "Идеальный борщ — классический рецепт", "username": "user3"},
    {"video_title": "Идеальный борщ — классический рецепт", "username": "user2"},
    {"video_title": "GTA 6 — Первый взгляд", "username": "user1"},
    {"video_title": "GTA 6 — Первый взгляд", "username": "user2"},
    {"video_title": "Топ-10 игр 2024 года", "username": "user1"},
    {"video_title": "Топ-10 игр 2024 года", "username": "user2"},
    {"video_title": "Топ-10 игр 2024 года", "username": "user3"},
    {"video_title": "Как собрать ПК для игр", "username": "user1"},
    {"video_title": "Как собрать ПК для игр", "username": "user2"},
]

TEST_SUBSCRIPTIONS = [
    {"subscriber_username": "user1", "channel_owner_username": "user2"},
    {"subscriber_username": "user1", "channel_owner_username": "user3"},
    {"subscriber_username": "user2", "channel_owner_username": "user1"},
    {"subscriber_username": "user2", "channel_owner_username": "user3"},
    {"subscriber_username": "user3", "channel_owner_username": "user1"},
    {"subscriber_username": "user3", "channel_owner_username": "user2"},
]


# ---------------------------------------------------------------------------
# Проверка состояния базы данных
# ---------------------------------------------------------------------------

TARGET_MODELS = (
    User,
    Channel,
    Video,
    Comment,
    Like,
    Subscription,
)


async def ensure_database_is_empty(session: AsyncSession) -> None:
    """Запретить заполнение, если целевые таблицы уже содержат данные."""
    for model in TARGET_MODELS:
        result = await session.scalar(
            select(model.id).limit(1)
        )

        if result is not None:
            raise RuntimeError(
                f"Таблица '{model.__tablename__}' уже содержит данные. "
                "Заполнение отменено во избежание конфликтов. "
                "Используйте пустую dev-базу данных."
            )


# ---------------------------------------------------------------------------
# Создание пользователей
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Создание каналов
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Создание видео
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Создание комментариев, лайков и подписок
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

async def seed_database() -> None:
    """Заполнить пустую базу данных тестовыми данными."""
    print("🚀 Запуск заполнения базы данных...")

    engine: AsyncEngine | None = None

    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
        )

        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with session_factory() as session:
            async with session.begin():
                await ensure_database_is_empty(session)

                users_by_username = await create_users(session)

                channels_by_owner_username = await create_channels(
                    session,
                    users_by_username,
                )

                videos_by_title = await create_videos(
                    session,
                    channels_by_owner_username,
                )

                await create_comments(
                    session,
                    users_by_username,
                    videos_by_title,
                )

                await create_likes(
                    session,
                    users_by_username,
                    videos_by_title,
                )

                await create_subscriptions(
                    session,
                    users_by_username,
                    channels_by_owner_username,
                )

        print("\n✅ База данных успешно заполнена!")
        print("\nСоздано:")
        print(f"  Пользователей: {len(TEST_USERS)}")
        print(f"  Каналов: {len(TEST_CHANNELS)}")
        print(f"  Видео: {len(TEST_VIDEOS)}")
        print(f"  Комментариев: {len(TEST_COMMENTS)}")
        print(f"  Лайков: {len(TEST_LIKES)}")
        print(f"  Подписок: {len(TEST_SUBSCRIPTIONS)}")

        print("\nТестовые учётные записи:")

        for user_data in TEST_USERS:
            print(
                f"  {user_data['username']}: "
                f"{user_data['password']}"
            )

    finally:
        if engine is not None:
            await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed_database())

    except IntegrityError as error:
        print("\n❌ Нарушено ограничение базы данных.")
        print(f"Подробности: {error.orig}")
        sys.exit(1)

    except Exception as error:
        print(f"\n❌ Ошибка заполнения базы данных: {error}")

        print("\nВозможные причины:")
        print("  1. PostgreSQL не запущен.")
        print("  2. Миграции Alembic не применены.")
        print("  3. Неверные настройки подключения в .env.")
        print("  4. Целевые таблицы уже содержат данные.")

        sys.exit(1)