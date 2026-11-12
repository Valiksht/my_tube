"""Скрипт для заполнения базы данных тестовыми данными.

Создаёт тестовых пользователей, каналы, видео, комментарии, лайки и подписки.
Запускается один раз после применения миграций.

Использование:
    python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

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
from app.models.users import User
from scripts.helpers import ensure_database_is_empty
from scripts.factories import (
    create_channels,
    create_comments,
    create_likes,
    create_subscriptions,
    create_users,
    create_videos,
)
from scripts.test_data import (
    TEST_CHANNELS,
    TEST_COMMENTS,
    TEST_LIKES,
    TEST_SUBSCRIPTIONS,
    TEST_USERS,
    TEST_VIDEOS,
)

DATABASE_URL = get_settings().database_url


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

    except Exception as error:
        print(f"\n❌ Ошибка заполнения базы данных: {error}")

        print("\nВозможные причины:")
        print("  1. PostgreSQL не запущен.")
        print("  2. Миграции Alembic не применены.")
        print("  3. Неверные настройки подключения в .env.")
        print("  4. Целевые таблицы уже содержат данные.")

        sys.exit(1)
