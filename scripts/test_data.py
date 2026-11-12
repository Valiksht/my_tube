"""Тестовые данные для заполнения базы данных.

Содержит константы TEST_USERS, TEST_CHANNELS, TEST_VIDEOS,
TEST_COMMENTS, TEST_LIKES, TEST_SUBSCRIPTIONS.
"""

from app.models.enum import UserRole, VideoPrivacy

# ---------------------------------------------------------------------------
# Пользователи
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

# ---------------------------------------------------------------------------
# Каналы
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Видео
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Комментарии
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Лайки
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Подписки
# ---------------------------------------------------------------------------

TEST_SUBSCRIPTIONS = [
    {"subscriber_username": "user1", "channel_owner_username": "user2"},
    {"subscriber_username": "user1", "channel_owner_username": "user3"},
    {"subscriber_username": "user2", "channel_owner_username": "user1"},
    {"subscriber_username": "user2", "channel_owner_username": "user3"},
    {"subscriber_username": "user3", "channel_owner_username": "user1"},
    {"subscriber_username": "user3", "channel_owner_username": "user2"},
]
