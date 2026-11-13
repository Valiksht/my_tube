# MyTube — YouTube Clone

## Запусп проекта без docker
chmod +x install.sh
./install.sh

## Если докер установлен
docker compose up --build -d

## Промты
Находятся в директории Promts
### 1
Сначала проект разрабатывался на локальной модели weine 3.5 9b с помощью cline
### 2
Далее из за постоянных зависаний и циклов модели, 
а так же её невозможности настроить запуск проекта
было решено перейти на gigacode в vs code.

## Стек технологий

### Backend
- Python 3.13
- FastAPI 0.115.x
- SQLAlchemy 2.1.8 (async)
- Alembic 1.20.1
- Pydantic 2.14.3

### Инфраструктура
- PostgreSQL 16
- Garage 2.2.0 (S3-compatible storage)
- Docker Compose

### Frontend
- Jinja2 3.1.4 (HTML templates)
- HTML5 / CSS
- Vanilla JavaScript

### Зависимости

| Пакет | Версия | Назначение |
|-------|--------|------------|
| fastapi | >=0.115.0,<0.116.0 | API framework |
| uvicorn | >=0.32.0 | ASGI server |
| starlette | >=0.37.0,<0.38.0 | ASGI foundation |
| SQLAlchemy | 2.1.8 | ORM |
| alembic | 1.20.1 | DB migrations |
| asyncpg | 0.30.0 | PostgreSQL driver |
| pydantic | 2.14.3 | Data validation |
| pydantic-settings | 2.16.2 | Settings via env vars |
| email-validator | >=2.1.0 | Email validation |
| annotated-types | 0.8.0 | Pydantic v2 type hints |
| python-multipart | 0.0.9 | Multipart form parsing |
| minio | >=7.1.0 | S3-compatible storage client |
| python-jose | >=3.3.0 | JWT tokens |
| passlib | 1.7.4 | Password hashing |
| bcrypt | 4.0.1 | Bcrypt backend |
| pillow | >=11.0.0 | Image processing |
| ffmpeg-python | >=0.2.0 | FFmpeg wrapper |
| jinja2 | 3.1.4 | HTML templates |
| python-dotenv | 1.2.4 | .env loading |
| pytest | 8.3.4 | Testing framework |
| httpx | 0.27.0 | Async HTTP client for tests |
| greenlet | 3.5.6 | SQLAlchemy async support |

## HTTP Эндпоинты

### REST API

#### Аутентификация — `/api/auth`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход (cookie + token) |
| POST | `/api/auth/logout` | Выход |
| GET | `/api/auth/me` | Текущий пользователь |
| GET | `/api/auth/check` | Проверка авторизации |

#### Видео — `/api/videos`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/videos` | Список публичных видео |
| GET | `/api/videos/search` | Поиск видео |
| GET | `/api/videos/{video_id}` | Видео по ID |
| POST | `/api/videos` | Создать запись видео |
| POST | `/api/videos/upload` | Загрузить видео с файлом |
| PATCH | `/api/videos/{video_id}` | Обновить видео |
| DELETE | `/api/videos/{video_id}` | Удалить видео |
| GET | `/api/videos/{video_id}/comments` | Комментарии видео |
| POST | `/api/videos/{video_id}/comments` | Создать комментарий |
| DELETE | `/api/videos/{video_id}/comments/{comment_id}` | Удалить комментарий |

#### Каналы и пользователи

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/channels/me` | Мой канал |
| POST | `/api/channels` | Создать канал |
| PATCH | `/api/channels/me` | Обновить канал |
| GET | `/api/channels/{channel_id}` | Канал по ID |
| GET | `/api/channels/{channel_id}/videos` | Видео канала |
| GET | `/api/users/me` | Данные пользователя |
| PATCH | `/api/users/me` | Обновить пользователя |
| GET | `/api/users/{user_id}` | Пользователь по ID |

#### Лайки — `/api/videos/{video_id}/likes`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/videos/{video_id}/likes` | Переключить лайк |
| GET | `/api/videos/{video_id}/likes/status` | Статус лайка |
| GET | `/api/videos/{video_id}/likes/count` | Количество лайков |

#### Подписки — `/api/channels/{channel_id}/subscriptions`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/channels/{channel_id}/subscriptions` | Переключить подписку |
| GET | `/api/channels/{channel_id}/subscriptions/status` | Статус подписки |
| GET | `/api/channels/{channel_id}/subscriptions/count` | Количество подписчиков |
| GET | `/api/channels/{channel_id}/subscriptions` | Список подписчиков |

#### Модерация — `/api/moderation`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/moderation/reports` | Создать жалобу |
| GET | `/api/moderation/reports/pending` | Жалобы на модерации |
| POST | `/api/moderation/reports/{report_id}/resolve` | Обработать жалобу |
| GET | `/api/moderation/hidden` | Скрытый контент |
| POST | `/api/moderation/hidden/{content_id}/unhide` | Восстановить контент |

#### Системный

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Проверка работоспособности |

### Frontend страницы

#### Аутентификация

| Method | Path | Description |
|--------|------|-------------|
| GET | `/login` | Страница входа |
| POST | `/login` | Обработка входа |
| GET | `/register` | Страница регистрации |
| POST | `/register` | Обработка регистрации |

#### Видео

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Главная страница |
| GET | `/upload` | Страница загрузки |
| POST | `/upload` | Обработка загрузки |
| GET | `/video/{video_id}` | Просмотр видео |
| GET | `/stream/{video_id}` | Потоковая передача (Range) |
| GET | `/search` | Поиск видео |

#### Каналы и профили

| Method | Path | Description |
|--------|------|-------------|
| GET | `/channel/create` | Создать канал |
| POST | `/channel/create` | Обработка создания |
| GET | `/channel/edit/{channel_id}` | Редактировать канал |
| POST | `/channel/edit/{channel_id}` | Обработка редактирования |
| GET | `/channel/{channel_id}` | Страница канала |
| GET | `/profile/{user_id}` | Профиль пользователя |

#### Подписки

| Method | Path | Description |
|--------|------|-------------|
| GET | `/my-subscriptions` | Мои подписки |

#### Модерация

| Method | Path | Description |
|--------|------|-------------|
| GET | `/moderation` | Панель модерации |
