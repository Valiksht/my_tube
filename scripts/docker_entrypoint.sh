#!/bin/bash
set -e

# ==================== Entry point для Docker-контейнера ====================
# 1. Ожидание готовности PostgreSQL
# 2. Применение миграций Alembic
# 3. Инициализация объектного хранилища
# 4. Загрузка тестовых данных
# 5. Запуск uvicorn

echo "============================================"
echo "  🚀 Запуск приложения MyTube..."
echo "============================================"

# --- 1. Ожидание PostgreSQL ---
echo ""
echo "⏳ Ожидание готовности PostgreSQL..."

MAX_RETRIES=30
RETRY_COUNT=0

while ! pg_isready -h "${POSTGRES_HOST:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Ошибка: Не удалось подключиться к PostgreSQL после ${MAX_RETRIES} попыток"
        exit 1
    fi
    
    echo "   Попытка ${RETRY_COUNT}/${MAX_RETRIES}..."
    sleep 2
done

echo "✅ PostgreSQL готов!"

# --- 2. Применение миграций Alembic ---
echo ""
echo "📦 Применение миграций Alembic..."

if alembic upgrade head; then
    echo "✅ Миграции применены успешно!"
else
    echo "❌ Ошибка при применении миграций"
    exit 1
fi

# --- 3. Ожидание готовых credentials Garage ---
echo ""
echo "⏳ Ожидание готовых credentials Garage..."

CRED_FILE="/garage_credentials/garage_credentials.env"
MAX_RETRIES=30
RETRY_COUNT=0

while [ ! -f "$CRED_FILE" ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Ошибка: Не удалось получить credentials Garage после ${MAX_RETRIES} попыток"
        exit 1
    fi
    
    echo "   Попытка ${RETRY_COUNT}/${MAX_RETRIES}..."
    sleep 2
done

echo "✅ Credentials Garage готовы!"

# --- 4. Инициализация объектного хранилища ---
echo ""
echo "🗄️  Инициализация объектного хранилища..."

STORAGE_TYPE="${STORAGE_TYPE:-garage}"

if [ "$STORAGE_TYPE" = "garage" ]; then
    if python scripts/init_storage.py; then
        echo "✅ Хранилище инициализировано!"
    else
        echo "⚠️  Предупреждение: Не удалось инициализировать хранилище (будет использован fallback)"
    fi
else
    echo "✅ Файловое хранилище используется (без инициализации)"
fi

# --- 5. Загрузка тестовых данных ---
echo ""
echo "🌱 Загрузка тестовых данных..."

if python scripts/seed_data.py; then
    echo "✅ Тестовые данные загружены!"
else
    echo "⚠️  Предупреждение: Не удалось загрузить тестовые данные (возможно, база уже заполнена)"
fi

# --- 6. Запуск uvicorn ---
echo ""
echo "============================================"
echo "  ✅ Приложение готово к работе!"
echo "============================================"
echo ""
echo "  🌐 Frontend:  http://localhost:8000"
echo "  📖 API docs:  http://localhost:8000/docs"
echo "  👤 Админ:     admin / admin123"
echo "  🔨 Модератор: moderator / mod123456"
echo ""
echo "============================================"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
