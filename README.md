# My Tube API - FastAPI Проект

Быстрая REST API платформа для видео-содержимого.

## 📁 Структура проекта

```
my_tube_2/
├── app/
│   ├── api/         # API endpoints (рути)
│   ├── core/        # Конфигурация и утилиты
│   ├── models/      # SQLAlchemy модели данных
│   ├── schemas/     # Pydantic схемы запросов/ответов
│   └── services/    # Сервисы (бизнес-логика)
├── main.py          # Точка входа приложения
├── requirements.txt # Зависимости проекта
└── README.md        # Документация
```

## 🚀 Запуск приложения

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск через uvicorn

```bash
uvicorn main:app --reload --port 8000
```

### Или с venv

```bash
# Создаем виртуальное окружение
python -m venv venv

# Активируем (Windows)
.\venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск
uvicorn main:app --reload --port 8000
```

## 📚 Описание директорий

### `app/api/`
- Места для API роутин (рути)
- Создавайте файлы вида `v1.py` или по модулям
- Используйте `include_router()` для подключения рутин

### `app/core/`
- **config.py** — настройка окружения, переменные
- **database.py** — подключение к базе данных SQLAlchemy
- **security.py** — JWT токены, проверка паролей
- **middleware.py** — промежуточное ПО (logging, cors и т.д.)

### `app/models/`
- Создавайте SQL модели с помощью SQLAlchemy
- Используйте ORM для работы с данными

### `app/schemas/`
- Pydantic модели для входящих запросов (Body)
- Pydantic модели для исходящих ответов
- Use model validators

### `app/services/`
- Храните бизнес-логику в сервисах
- Изолируйте роутин от логики
- Например: `user_service.py`, `auth_service.py`

## 🔧 Тестирование

```bash
# Установка pytest и инструментов для тестов
pip install pytest httpx

# Запуск тестов
pytest -v
```

## 📖 Пример использования

1. В файле `app/api/users.py`:

```python
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Пользователи"])

@router.post("")
async def create_user(user_data: UserCreate, db=Depends(get_db)):
    # бизнес-логика из сервиса...
```

2. Подключите роут в `app/api/__init__.py`:

```python
from fastapi import APIRouter
from app.api.users import router

api_router = APIRouter()
api_router.include_router(router, prefix="/v1")
```

## 📧 Контакты

Для вопросов и предложений — [GitHub Issues](https://github.com/...)