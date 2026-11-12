#!/bin/bash
set -e

# ==================== Entry point для Production Docker-контейнера ====================
# 1. Ожидание готовности PostgreSQL
# 2. Применение миграций Alembic
# 3. Загрузка тестовых данных
# 4. Запуск uvicorn

echo "============================================"
echo "  🚀 Запуск приложения MyTube (Production)..."
echo "============================================"

# --- 1. Ожидание PostgreSQL ---
echo ""
echo "⏳ Ожидание готовности PostgreSQL..."

MAX_RETRIES=30
RETRY_COUNT=0

# Используем переменные окружения напрямую
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-postgres}"

while ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" > /dev/null 2>&1; do
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

# --- 3. Загрузка тестовых данных ---
echo ""
echo "🌱 Загрузка тестовых данных..."

if python scripts/seed_data.py; then
    echo "✅ Тестовые данные загружены!"
else
    echo "⚠️  Предупреждение: Не удалось загрузить тестовые данные (возможно, база уже заполнена)"
fi

# --- 4. Запуск uvicorn ---
echo ""
echo "============================================"
echo "  ✅ Приложение готово к работе!"
echo "============================================"
echo ""
echo "  🌐 Frontend:  http://localhost:8000"
echo "  📖 API docs:  http://localhost:8000/docs"
echo ""
echo "============================================"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
