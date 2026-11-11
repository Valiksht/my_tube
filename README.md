# YouTube Clone

Учебный проект — клон YouTube с основными функциями видеохостинга.

## Возможности

- Регистрация и вход в аккаунт
- Создание канала
- Загрузка видео
- Просмотр видео с видеоплеером
- Лайки и комментарии
- Подписка на каналы
- Поиск видео по названию
- Приватные видео (public/unlisted/private)
- Система модерации (жалобы, скрытие контента)
- Роли: user, moderator, admin

## Технологии

**Backend:**
- Python 3.13
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic (миграции)
- Pydantic

**Хранение видео:**
- MinIO (S3-совместимое хранилище)
- FFmpeg (обработка видео, создание превью)

**Инфраструктура:**
- Docker
- Docker Compose

**Frontend:**
- Jinja2 шаблоны
- HTML5/CSS/JavaScript

## Установка и запуск

### Требования

- **Docker** и **Docker Compose** (обязательно)
- **Python 3.13+** (для локальной разработки)
- **FFmpeg** (опционально, для обработки видео)

### Быстрый старт (Docker)

#### 1. Клонируйте репозиторий

```powershell
git clone <repository-url>
cd my_tube_2
```

#### 2. Настройте окружение

```powershell
copy .env.example .env
```

Откройте `.env` и при необходимости измените настройки:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mytube_db

# MinIO (объектное хранилище)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=videos
```

#### 3. Запустите сервисы через Docker

```powershell
docker compose up -d
```

Это запустит:
- **PostgreSQL** на порту `5432`
- **MinIO** на порту `9000` (API) и `9001` (консоль)

Проверьте, что контейнеры работают:

```powershell
docker compose ps
```

#### 4. Примените миграции базы данных

```powershell
venv/Scripts/python.exe -m alembic upgrade head
```

#### 5. Заполните базу тестовыми данными (опционально)

```powershell
venv/Scripts/python.exe scripts/seed_data.py
```

#### 6. Запустите приложение

```powershell
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

#### 7. Откройте в браузере

| Адрес | Описание |
|-------|----------|
| http://localhost:8000 | Главное приложение |
| http://localhost:8000/docs | API документация (Swagger) |
| http://localhost:9001 | MinIO Console (логин: `minioadmin`, пароль: `minioadmin`) |

### Локальная разработка (без Docker)

Если PostgreSQL и MinIO уже запущены локально:

```powershell
# 1. Установите зависимости
venv/Scripts/python.exe -m pip install -r requirements.txt

# 2. Примените миграции
venv/Scripts/python.exe -m alembic upgrade head

# 3. Запустите приложение
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

---

## Тестовые аккаунты

После запуска `scripts/seed_data.py` доступны следующие аккаунты:

| Логин | Пароль | Роль | Описание |
|-------|--------|------|----------|
| `admin` | `admin123` | admin | Администратор |
| `moderator` | `mod123456` | moderator | Модератор |
| `user1` | `user123456` | user | Обычный пользователь |
| `user2` | `user123456` | user | Второй пользователь |
| `user3` | `user123456` | user | Третий пользователь |

---

## Структура проекта

```
my_tube_2/
├── alembic/                    # Миграции базы данных
│   ├── env.py
│   └── versions/
│       └── 8817bb8f02d3_initial_schema.py
├── app/
│   ├── api/                    # API роутеры (6 файлов)
│   │   ├── auth.py             # Регистрация, вход, выход
│   │   ├── videos.py           # CRUD видео, комментарии
│   │   ├── likes.py            # Лайки
│   │   ├── subscriptions.py    # Подписки
│   │   ├── channels.py         # Каналы и пользователи
│   │   └── moderation.py       # Модерация
│   ├── core/                   # Core модули (4 файла)
│   │   ├── config.py           # Настройки приложения
│   │   ├── security.py         # Хеширование паролей, JWT
│   │   ├── csrf.py             # CSRF защита
│   │   └── exceptions.py       # Общие исключения
│   ├── crud/                   # CRUD операции (7 файлов)
│   │   ├── base.py             # Базовый репозиторий
│   │   ├── user.py             # Пользователи
│   │   ├── channel.py          # Каналы
│   │   ├── video.py            # Видео
│   │   ├── comment.py          # Комментарии
│   │   ├── like.py             # Лайки
│   │   └── subscription.py     # Подписки
│   ├── database/               # Настройка БД (3 файла)
│   │   ├── config.py           # Подключение к PostgreSQL
│   │   ├── session.py          # AsyncSession
│   │   └── dependencies.py     # Зависимости FastAPI
│   ├── models/                 # SQLAlchemy модели (10 файлов)
│   │   ├── users.py            # Пользователи
│   │   ├── channel.py          # Каналы
│   │   ├── video.py            # Видео
│   │   ├── comment.py          # Комментарии
│   │   ├── like.py             # Лайки
│   │   ├── subscription.py     # Подписки
│   │   ├── session.py          # Сессии авторизации
│   │   ├── moderation.py       # Жалобы и скрытый контент
│   │   ├── enum.py             # Перечисления
│   │   └── base.py             # Базовый класс
│   ├── schemas/                # Pydantic схемы (7 файлов)
│   │   ├── auth.py             # Авторизация
│   │   ├── user.py             # Пользователи
│   │   ├── channel.py          # Каналы
│   │   ├── video.py            # Видео
│   │   ├── comment.py          # Комментарии
│   │   ├── like.py             # Лайки
│   │   └── subscription.py     # Подписки
│   ├── services/               # Бизнес-логика (8 файлов)
│   │   ├── auth.py             # Аутентификация
│   │   ├── video.py            # Операции с видео
│   │   ├── comment.py          # Комментарии
│   │   ├── like.py             # Лайки
│   │   ├── subscription.py     # Подписки
│   │   ├── moderation.py       # Модерация
│   │   └── video_processing.py # FFmpeg обработка
│   ├── static/                 # Статические файлы
│   │   ├── css/style.css       # Стили (~400 строк)
│   │   └── js/app.js           # JavaScript
│   ├── storage/                # Объектное хранилище
│   │   ├── base.py             # Базовый класс
│   │   └── minio.py            # Реализация MinIO
│   ├── templates/              # Jinja2 шаблоны (7 файлов)
│   │   ├── base.html           # Базовый шаблон
│   │   ├── index.html          # Главная страница
│   │   ├── login.html          # Страница входа
│   │   ├── register.html       # Страница регистрации
│   │   ├── video.html          # Страница просмотра
│   │   ├── upload.html         # Страница загрузки
│   │   └── profile.html        # Страница профиля
│   └── main.py                 # Главный файл приложения
├── scripts/                    # Вспомогательные скрипты
│   └── seed_data.py            # Заполнение тестовыми данными
├── tests/                      # Тесты
│   ├── conftest.py             # Общие fixtures
│   ├── test_auth.py            # Тесты аутентификации
│   └── test_videos.py          # Тесты видео
├── .env                        # Переменные окружения
├── .env.example                # Пример переменных
├── docker-compose.yaml         # Docker конфигурация
├── Dockerfile                  # Образ приложения
├── alembic.ini                 # Alembic конфигурация
├── requirements.txt            # Зависимости Python
└── README.md                   # Этот файл
```

---

## API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/auth/register` | Регистрация нового пользователя |
| `POST` | `/api/auth/login` | Вход в аккаунт |
| `POST` | `/api/auth/logout` | Выход из аккаунта |
| `GET` | `/api/auth/me` | Данные текущего пользователя |
| `GET` | `/api/auth/check` | Проверка авторизации |

### Видео

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/videos` | Список публичных видео |
| `GET` | `/api/videos/search` | Поиск видео по названию |
| `GET` | `/api/videos/{id}` | Получить видео по ID |
| `POST` | `/api/videos` | Создать видео |
| `POST` | `/api/videos/upload` | Загрузить видео с файлом |
| `PATCH` | `/api/videos/{id}` | Обновить видео |
| `DELETE` | `/api/videos/{id}` | Удалить видео |

### Комментарии

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/videos/{id}/comments` | Комментарии видео |
| `POST` | `/api/videos/{id}/comments` | Создать комментарий |
| `DELETE` | `/api/videos/{id}/comments/{comment_id}` | Удалить комментарий |

### Лайки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/videos/{id}/likes` | Переключить лайк |
| `GET` | `/api/videos/{id}/likes/status` | Проверить лайк |
| `GET` | `/api/videos/{id}/likes/count` | Количество лайков |

### Подписки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/channels/{id}/subscriptions` | Подписаться на канал |
| `GET` | `/api/channels/{id}/subscriptions/status` | Проверить подписку |
| `GET` | `/api/channels/{id}/subscriptions/count` | Количество подписчиков |
| `GET` | `/api/channels/{id}/subscriptions` | Список подписчиков |

### Каналы и пользователи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/channels/me` | Мой канал |
| `POST` | `/api/channels` | Создать канал |
| `PATCH` | `/api/channels/me` | Обновить канал |
| `GET` | `/api/channels/{id}` | Получить канал |
| `GET` | `/api/channels/{id}/videos` | Видео канала |
| `GET` | `/api/users/{id}` | Получить пользователя |
| `GET` | `/api/users/me` | Текущий пользователь |
| `PATCH` | `/api/users/me` | Обновить профиль |

### Модерация (требует роль moderator/admin)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/moderation/reports/pending` | Жалобы на модерации |
| `POST` | `/api/moderation/reports/{id}/resolve` | Обработать жалобу |
| `GET` | `/api/moderation/hidden` | Скрытый контент |
| `POST` | `/api/moderation/hidden/{id}/unhide` | Восстановить контент |

---

## Тестирование

### Запуск всех тестов

```powershell
venv/Scripts/python.exe -m pytest
```

### Запуск с подробным выводом

```powershell
venv/Scripts/python.exe -m pytest -v
```

### Запуск конкретных тестов

```powershell
# Тесты аутентификации
venv/Scripts/python.exe -m pytest tests/test_auth.py -v

# Тесты видео
venv/Scripts/python.exe -m pytest tests/test_videos.py -v
```

### Запуск с покрытием

```powershell
venv/Scripts/python.exe -m pytest --cov=app --cov-report=html
```

---

## Роли пользователей

| Роль | Описание | Права |
|------|----------|-------|
| **user** | Обычный пользователь | Загрузка видео, комментарии, лайки, подписки |
| **moderator** | Модератор | Все права user + скрытие контента, обработка жалоб |
| **admin** | Администратор | Полные права управления системой |

---

## Приватность видео

| Тип | Описание | Кто видит |
|-----|----------|-----------|
| **public** | Публичное | Все пользователи |
| **unlisted** | Не в списке | Все, у кого есть ссылка |
| **private** | Приватное | Только владелец |

---

## Безопасность

| Механизм | Описание |
|----------|----------|
| **Хеширование паролей** | bcrypt через passlib |
| **Серверные сессии** | HttpOnly Cookie с криптографическим session_id |
| **CSRF защита** | Double cookie validation pattern |
| **Роли и права** | Проверка на backend для каждого защищённого действия |
| **Приватные видео** | Проверка доступа перед выдачей файла |
| **Секреты в .env** | Пароли и ключи не хранятся в коде |

---

## Устранение проблем

### Ошибка подключения к базе данных

```powershell
# Проверьте, что PostgreSQL запущен
docker compose ps

# Перезапустите PostgreSQL
docker compose restart postgres

# Проверьте логи
docker compose logs postgres
```

### Ошибка миграций

```powershell
# Проверьте текущую версию миграции
venv/Scripts/python.exe -m alembic current

# Если нужно откатить
venv/Scripts/python.exe -m alembic downgrade base

# Примените миграции заново
venv/Scripts/python.exe -m alembic upgrade head
```

### Ошибка подключения к MinIO

```powershell
# Проверьте, что MinIO запущен
docker compose ps minio

# Проверьте логи
docker compose logs minio

# Проверьте, что бакет создан
docker compose exec minio mc ls local/videos
```

### Приложение не запускается

```powershell
# Проверьте, что зависимости установлены
venv/Scripts/python.exe -m pip install -r requirements.txt

# Проверьте синтаксис
venv/Scripts/python.exe -m py_compile app/main.py

# Проверьте импорты
venv/Scripts/python.exe -c "from app.main import app; print('OK')"
```

---

## Лицензия

Учебный проект.
