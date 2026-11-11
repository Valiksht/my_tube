# YouTube Clone

Учебный проект — клон YouTube с основными функциями видеохостинга.

---

## 🚀 Production — Развёртывание на сервере

Один файл `docker-compose.production.yaml` запускает полный стек: PostgreSQL + MinIO + API + Nginx.

### Требования

- Ubuntu 22.04+ (или любой Linux с Docker)
- Docker 24+ и Docker Compose v2
- 2 ГБ RAM минимум

### Шаг 1: Клонируйте проект

```bash
git clone <repository-url>
cd my_tube_2
```

### Шаг 2: Настройте production окружение

```bash
cp .env.production .env
```

Откройте `.env` и измените значения на production-версии:

```env
# Безопасные пароли (сгенерируйте свои!)
POSTGRES_PASSWORD=CHANGE_THIS_SECURE_PASSWORD_123
SECRET_KEY=CHANGE_THIS_PRODUCTION_SECRET_KEY
CSRF_SECRET_KEY=CHANGE_THIS_PRODUCTION_CSRF_KEY

# Ваш домен
CORS_ORIGINS=https://yourdomain.com

# MinIO
MINIO_ROOT_USER=CHANGE_THIS_MINIO_USER
MINIO_ROOT_PASSWORD=CHANGE_THIS_MINIO_PASSWORD
```

> **Важно:** Сгенерируйте секретные ключи:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### Шаг 3: Запустите стек

```bash
docker compose -f docker-compose.production.yaml up -d --build
```

Это запустит:

| Сервис | Порт | Описание |
|--------|------|----------|
| PostgreSQL | 5432 | База данных |
| MinIO | 9000 / 9001 | Хранилище (API / Console) |
| API | 8000 | FastAPI приложение |
| Nginx | 80 | Reverse proxy |

### Шаг 4: Примените миграции

```bash
docker compose -f docker-compose.production.yaml exec api \
    alembic upgrade head
```

### Шаг 5: Заполните тестовыми данными

```bash
docker compose -f docker-compose.production.yaml exec api \
    python scripts/seed_data.py
```

### Шаг 6: Откройте в браузере

| Адрес | Описание |
|-------|----------|
| http://yourdomain.com | Главное приложение |
| http://yourdomain.com/docs | API документация (Swagger) |
| http://yourdomain.com:9001 | MinIO Console |

### Управление

```bash
# Перезапуск
docker compose -f docker-compose.production.yaml restart

# Остановка
docker compose -f docker-compose.production.yaml down

# Логи
docker compose -f docker-compose.production.yaml logs -f api

# Масштабирование API (4 воркера)
docker compose -f docker-compose.production.yaml up -d --scale api=4
```

### Минимальная конфигурация сервера

```
CPU: 2 ядра
RAM: 2 ГБ
Disk: 20 ГБ
OS: Ubuntu 22.04 LTS
```

---

## 💻 Локальная разработка

Запуск с PostgreSQL и MinIO в Docker, код — на хосте с hot-reload.

### Требования

- Docker и Docker Compose
- Python 3.13+
- FFmpeg (опционально, для обработки видео)

### Шаг 1: Клонируйте и настройте

```powershell
git clone <repository-url>
cd my_tube_2

copy .env.example .env
```

### Шаг 2: Запустите инфраструктуру

```powershell
docker compose up -d
```

Запускает PostgreSQL и MinIO. Проверьте:

```powershell
docker compose ps
```

### Шаг 3: Настройте виртуальное окружение

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Шаг 4: Примените миграции

```powershell
venv/Scripts/python.exe -m alembic upgrade head
```

### Шаг 5: Заполните тестовыми данными

```powershell
venv/Scripts/python.exe scripts/seed_data.py
```

Доступные аккаунты:

| Логин | Пароль | Роль |
|-------|--------|------|
| `admin` | `admin123` | admin |
| `moderator` | `mod123456` | moderator |
| `user1` | `user123456` | user |

### Шаг 6: Запустите приложение

```powershell
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

### Шаг 7: Откройте в браузере

| Адрес | Описание |
|-------|----------|
| http://localhost:8000 | Главное приложение |
| http://localhost:8000/docs | API документация (Swagger) |
| http://localhost:9001 | MinIO Console |

### Тестирование

```powershell
# Все тесты
venv/Scripts/python.exe -m pytest

# Подробный вывод
venv/Scripts/python.exe -m pytest -v

# Конкретный файл
venv/Scripts/python.exe -m pytest tests/test_auth.py -v

# С покрытием
venv/Scripts/python.exe -m pytest --cov=app --cov-report=html
```

---

## 📦 Стек технологий

### Backend

| Технология | Назначение |
|------------|-----------|
| **Python 3.13** | Язык программирования |
| **FastAPI** | Web-фреймворк |
| **SQLAlchemy 2.0** | ORM (async) |
| **PostgreSQL 15** | База данных |
| **Alembic** | Миграции БД |
| **Pydantic v2** | Валидация данных |
| **passlib + bcrypt** | Хеширование паролей |
| **python-jose** | JWT токены |

### Хранение и обработка

| Технология | Назначение |
|------------|-----------|
| **MinIO** | S3-совместимое хранилище |
| **FFmpeg** | Обработка видео, превью |

### Инфраструктура

| Технология | Назначение |
|------------|-----------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Оркестрация сервисов |
| **Nginx** | Reverse proxy |

### Frontend

| Технология | Назначение |
|------------|-----------|
| **Jinja2** | Шаблоны |
| **HTML5 / CSS** | Вёрстка |
| **JavaScript** | Интерактивность |

### Тестирование

| Технология | Назначение |
|------------|-----------|
| **pytest** | Фреймворк тестов |
| **httpx** | HTTP-клиент для тестов |

---

## 📁 Структура проекта

```
my_tube_2/
├── alembic/                    # Миграции базы данных
├── app/
│   ├── api/                    # API роутеры
│   ├── core/                   # Конфигурация, безопасность
│   ├── crud/                   # CRUD операции
│   ├── database/               # Настройка БД
│   ├── models/                 # SQLAlchemy модели
│   ├── schemas/                # Pydantic схемы
│   ├── services/               # Бизнес-логика
│   ├── static/                 # CSS, JS
│   ├── storage/                # Объектное хранилище
│   ├── templates/              # Jinja2 шаблоны
│   └── main.py                 # Главный файл
├── scripts/                    # Вспомогательные скрипты
├── tests/                      # Тесты
├── docker-compose.production.yaml  # Production стек
├── docker-compose.yaml         # Локальная инфраструктура
├── Dockerfile.production       # Production образ
├── requirements.txt            # Зависимости Python
├── .env.production             # Production окружение
└── README.md                   # Документация
```

---

## 🔐 Безопасность

- bcrypt хеширование паролей
- Серверные сессии с HttpOnly Cookie
- CSRF защита
- Проверка прав на backend
- Приватные видео с проверкой доступа
- Секреты хранятся в `.env`, не в коде

---

## 📝 Лицензия

Учебный проект.
