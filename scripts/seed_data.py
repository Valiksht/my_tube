"""Скрипт для заполнения базы данных тестовыми данными.

Создаёт тестовых пользователей, каналы, видео, комментарии, лайки и подписки.
Запускается один раз после применения миграций.

Использование:
    python scripts/seed_data.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.users import User
from app.models.channel import Channel
from app.models.video import Video
from app.models.comment import Comment
from app.models.like import Like
from app.models.subscription import Subscription
from app.models.enum import UserRole, VideoPrivacy


# Получаем DATABASE_URL из общей конфигурации приложения
_settings = get_settings()
DATABASE_URL = _settings.database_url

# Тестовые данные
TEST_USERS = [
    {
        "username": "admin",
        "email": "admin@mytube.com",
        "password": "admin123",
        "role": "admin",
    },
    {
        "username": "moderator",
        "email": "mod@mytube.com",
        "password": "mod123456",
        "role": "moderator",
    },
    {
        "username": "user1",
        "email": "user1@mytube.com",
        "password": "user123456",
        "role": "user",
    },
    {
        "username": "user2",
        "email": "user2@mytube.com",
        "password": "user123456",
        "role": "user",
    },
    {
        "username": "user3",
        "email": "user3@mytube.com",
        "password": "user123456",
        "role": "user",
    },
]

TEST_CHANNELS = [
    {
        "user_id": 1,
        "name": "Admin Channel",
        "description": "Официальный канал администратора",
    },
    {
        "user_id": 2,
        "name": "Moderator Hub",
        "description": "Канал модератора",
    },
    {
        "user_id": 3,
        "name": "Tech Reviews",
        "description": "Обзоры технологий и гаджетов",
    },
    {
        "user_id": 4,
        "name": "Cooking Master",
        "description": "Кулинарные рецепты и советы",
    },
    {
        "user_id": 5,
        "name": "Gaming Zone",
        "description": "Игровые обзоры и стримы",
    },
]

TEST_VIDEOS = [
    {
        "channel_id": 3,
        "title": "Обзор iPhone 15 Pro Max",
        "description": "Подробный обзор нового флагмана Apple. Рассматриваем камеру, производительность, батарею и все новые функции.",
        "privacy": "public",
        "duration": 845,
        "view_count": 15420,
        "is_published": True,
    },
    {
        "channel_id": 3,
        "title": "Лучшие смартфоны 2024 года",
        "description": "Топ-10 смартфонов этого года. Сравнение камер, производительности и цены.",
        "privacy": "public",
        "duration": 1230,
        "view_count": 8930,
        "is_published": True,
    },
    {
        "channel_id": 3,
        "title": "Как выбрать ноутбук в 2024",
        "description": "Гайд по выбору ноутбука: от бюджетных до игровых моделей.",
        "privacy": "public",
        "duration": 960,
        "view_count": 5670,
        "is_published": True,
    },
    {
        "channel_id": 4,
        "title": "Идеальный борщ — классический рецепт",
        "description": "Учимся готовить настоящий борщ по бабушкиному рецепту. Секреты приготовления.",
        "privacy": "public",
        "duration": 720,
        "view_count": 23100,
        "is_published": True,
    },
    {
        "channel_id": 4,
        "title": "5 рецептов за 15 минут",
        "description": "Быстрые и вкусные рецепты для тех, кто не любит тратить время на кухне.",
        "privacy": "public",
        "duration": 900,
        "view_count": 18750,
        "is_published": True,
    },
    {
        "channel_id": 4,
        "title": "Домашний хлеб без дрожжей",
        "description": "Простой рецепт вкусного домашнего хлеба без использования дрожжей.",
        "privacy": "public",
        "duration": 540,
        "view_count": 12300,
        "is_published": True,
    },
    {
        "channel_id": 5,
        "title": "GTA 6 — Первый взгляд",
        "description": "Анализируем первый трейлер GTA 6. Всё что мы знаем о игре.",
        "privacy": "public",
        "duration": 680,
        "view_count": 45200,
        "is_published": True,
    },
    {
        "channel_id": 5,
        "title": "Топ-10 игр 2024 года",
        "description": "Лучшие игры этого года по версии нашего канала.",
        "privacy": "public",
        "duration": 1500,
        "view_count": 32100,
        "is_published": True,
    },
    {
        "channel_id": 5,
        "title": "Как собрать ПК для игр",
        "description": "Полное руководство по сборке игрового компьютера: от выбора комплектующих до настройки.",
        "privacy": "public",
        "duration": 2100,
        "view_count": 28900,
        "is_published": True,
    },
    {
        "channel_id": 3,
        "title": "Секретный проект",
        "description": "Это приватное видео, видимое только владельцу канала.",
        "privacy": "private",
        "duration": 300,
        "view_count": 0,
        "is_published": False,
    },
]

TEST_COMMENTS = [
    {"video_id": 1, "user_id": 4, "content": "Отличный обзор! Ждал выхода этого телефона."},
    {"video_id": 1, "user_id": 5, "content": "Камера просто огонь 🔥"},
    {"video_id": 2, "user_id": 3, "content": "Согласен с рейтингом, но Sony была бы выше."},
    {"video_id": 4, "user_id": 3, "content": "Попробовала по рецепту — получилось идеально!"},
    {"video_id": 4, "user_id": 5, "content": "Бабушка такой же борщ готовила 😊"},
    {"video_id": 5, "user_id": 4, "content": "Рецепт №3 — мой любимый, готовлю каждую неделю."},
    {"video_id": 7, "user_id": 3, "content": "Наконец-то дождались! GTA 6 будет топ."},
    {"video_id": 7, "user_id": 4, "content": "Графика выглядит невероятно!"},
    {"video_id": 8, "user_id": 5, "content": "Elden Ring заслуживал первого места!"},
    {"video_id": 9, "user_id": 3, "content": "Собрал ПК по гайду — работает отлично!"},
    {"video_id": 1, "user_id": 3, "content": "Можно ли сравнить с Samsung S24?"},
    {"video_id": 6, "user_id": 4, "content": "Хлеб получился супер, спасибо за рецепт!"},
    {"video_id": 10, "user_id": 5, "content": "Когда релиз GTA 6?"},
    {"video_id": 3, "user_id": 4, "content": "Беру MacBook Air M3, рекомендую!"},
    {"video_id": 8, "user_id": 3, "content": "Cyberpunk 2077 — моя игра года!"},
]

TEST_LIKES = [
    {"video_id": 1, "user_id": 4},
    {"video_id": 1, "user_id": 5},
    {"video_id": 1, "user_id": 3},
    {"video_id": 2, "user_id": 3},
    {"video_id": 2, "user_id": 5},
    {"video_id": 4, "user_id": 3},
    {"video_id": 4, "user_id": 5},
    {"video_id": 4, "user_id": 4},
    {"video_id": 7, "user_id": 3},
    {"video_id": 7, "user_id": 4},
    {"video_id": 8, "user_id": 3},
    {"video_id": 8, "user_id": 4},
    {"video_id": 8, "user_id": 5},
    {"video_id": 9, "user_id": 3},
    {"video_id": 9, "user_id": 4},
]

TEST_SUBSCRIPTIONS = [
    {"subscribed_user_id": 3, "subscribed_channel_id": 4},
    {"subscribed_user_id": 3, "subscribed_channel_id": 5},
    {"subscribed_user_id": 4, "subscribed_channel_id": 3},
    {"subscribed_user_id": 4, "subscribed_channel_id": 5},
    {"subscribed_user_id": 5, "subscribed_channel_id": 3},
    {"subscribed_user_id": 5, "subscribed_channel_id": 4},
]


async def seed_database():
    """Заполнить базу данных тестовыми данными."""
    print("🚀 Запуск скрипта заполнения базы данных...")
    
    # Создаём движок
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем, есть ли уже данные
        from sqlalchemy import select, func
        
        user_count = await session.execute(select(func.count()).select_from(User))
        if user_count.scalar() > 0:
            print("⚠️  База данных уже содержит данные. Пропускаем.")
            await engine.dispose()
            return
        
        print("\n📝 Создание пользователей...")
        users = []
        for user_data in TEST_USERS:
            hashed_pw = hash_password(user_data["password"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_pw,
                role=user_data["role"],
                is_active=True,
            )
            session.add(user)
            users.append(user)
        
        await session.flush()
        print(f"   ✅ Создано {len(users)} пользователей")
        
        # Выводим учётные данные
        print("\n🔑 Учётные данные пользователей:")
        for user in users:
            print(f"   • {user.username} / {user.email} / пароль: {TEST_USERS[user.id - 1]['password']} (роль: {user.role})")
        
        print("\n📺 Создание каналов...")
        channels = []
        for i, channel_data in enumerate(TEST_CHANNELS):
            channel = Channel(
                user_id=channel_data["user_id"],
                name=channel_data["name"],
                description=channel_data["description"],
            )
            session.add(channel)
            channels.append(channel)
        
        await session.flush()
        print(f"   ✅ Создано {len(channels)} каналов")
        
        print("\n🎬 Создание видео...")
        videos = []
        for video_data in TEST_VIDEOS:
            video = Video(
                channel_id=video_data["channel_id"],
                title=video_data["title"],
                description=video_data["description"],
                privacy=video_data["privacy"],
                duration=video_data["duration"],
                view_count=video_data["view_count"],
                is_published=video_data["is_published"],
            )
            session.add(video)
            videos.append(video)
        
        await session.flush()
        print(f"   ✅ Создано {len(videos)} видео")
        
        print("\n💬 Создание комментариев...")
        comments = []
        for comment_data in TEST_COMMENTS:
            comment = Comment(
                video_id=comment_data["video_id"],
                user_id=comment_data["user_id"],
                content=comment_data["content"],
            )
            session.add(comment)
            comments.append(comment)
        
        await session.flush()
        print(f"   ✅ Создано {len(comments)} комментариев")
        
        print("\n👍 Создание лайков...")
        for like_data in TEST_LIKES:
            like = Like(
                video_id=like_data["video_id"],
                user_id=like_data["user_id"],
            )
            session.add(like)
        
        print(f"   ✅ Создано {len(TEST_LIKES)} лайков")
        
        print("\n🔔 Создание подписок...")
        for sub_data in TEST_SUBSCRIPTIONS:
            subscription = Subscription(
                subscribed_user_id=sub_data["subscribed_user_id"],
                subscribed_channel_id=sub_data["subscribed_channel_id"],
            )
            session.add(subscription)
        
        print(f"   ✅ Создано {len(TEST_SUBSCRIPTIONS)} подписок")
        
        # Финальный commit
        await session.commit()
        
        print("\n" + "=" * 60)
        print("✅ База данных успешно заполнена!")
        print("=" * 60)
        print(f"\n📊 Итого создано:")
        print(f"   • Пользователей: {len(users)}")
        print(f"   • Каналов: {len(channels)}")
        print(f"   • Видео: {len(videos)}")
        print(f"   • Комментариев: {len(comments)}")
        print(f"   • Лайков: {len(TEST_LIKES)}")
        print(f"   • Подписок: {len(TEST_SUBSCRIPTIONS)}")
        print("\n🌐 Приложение доступно: http://localhost:8000")
        print("📖 API документация: http://localhost:8000/docs")
        print("=" * 60)
    
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n📋 Возможные причины:")
        print("   1. PostgreSQL не запущен (docker compose up -d)")
        print("   2. Миграции не применены (alembic upgrade head)")
        print("   3. Неверные настройки в .env")
        sys.exit(1)
