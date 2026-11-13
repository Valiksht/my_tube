#!/bin/bash
set -Eeuo pipefail

echo "========================================"
echo "Starting MyTube..."
echo "========================================"

# 1. Wait for PostgreSQL
echo "Waiting for PostgreSQL..."

MAX_RETRIES=30

for ((i=1; i<=MAX_RETRIES; i++)); do
    if pg_isready \
        -h "${POSTGRES_HOST:-postgres}" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "${POSTGRES_USER:-postgres}" \
        -d "${POSTGRES_DB:-mytube_db}" \
        >/dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi

    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "PostgreSQL connection failed."
        exit 1
    fi

    sleep 2
done

# 2. Create storage directory
mkdir -p "${STORAGE_DIR:-/app/storage}"

echo "Filesystem storage ready."

# 3. Apply database migrations
echo "Applying Alembic migrations..."

alembic upgrade head

echo "Migrations applied."

# 4. Start application
echo "Starting FastAPI..."

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000
