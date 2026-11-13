#!/bin/sh
# Скрипт инициализации Garage v2.2.0
# Запускается один раз после первого старта Garage
# Идентипотентный — можно запускать многократно

set -e

echo "============================================"
echo "  Инициализация Garage v2.2.0"
echo "============================================"

GARAGE_HOST="${GARAGE_HOST:-garage}"

# --- Ожидание готовности S3 API (порт 3900) ---
echo ""
echo "Ожидание готовности Garage S3 API (порт 3900)..."

MAX_RETRIES=60
RETRY_COUNT=0

while ! nc -z -w2 $GARAGE_HOST 3900 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Ошибка: Не удалось подключиться к Garage S3 API после ${MAX_RETRIES} попыток"
        exit 1
    fi
    
    sleep 2
done

echo "Garage S3 API доступен!"

# --- Ожидание готовности RPC (порт 3901) ---
echo ""
echo "Ожидание готовности Garage RPC (порт 3901)..."

RPC_MAX_RETRIES=60
RPC_RETRY_COUNT=0

while ! nc -z -w2 $GARAGE_HOST 3901 2>/dev/null; do
    RPC_RETRY_COUNT=$((RPC_RETRY_COUNT + 1))
    
    if [ $RPC_RETRY_COUNT -ge $RPC_MAX_RETRIES ]; then
        echo "Ошибка: Не удалось подключиться к Garage RPC после ${RPC_MAX_RETRIES} попыток"
        exit 1
    fi
    
    sleep 2
done

echo "Garage RPC готов!"

# --- Получение ID ноды из running-контейнера Garage ---
echo ""
echo "Поиск ноды Garage..."

NODE_ID=""
NODE_LIST_RETRIES=20
NODE_LIST_COUNT=0

while [ -z "$NODE_ID" ]; do
    NODE_LIST_COUNT=$((NODE_LIST_COUNT + 1))
    echo "Поиск ноды: попытка $NODE_LIST_COUNT/$NODE_LIST_RETRIES..."
    
    # Получаем список нод через Docker exec
    NODE_LIST_OUTPUT=$(docker exec mytube_garage_local /garage node list 2>&1 | grep -v '^\[2m' | grep -v '^\[0m' || true)
    
    # Пытаемся извлечь ID ноды из вывода
    # Формат вывода: <node_id>@<host>:<port>
    NODE_ID=$(echo "$NODE_LIST_OUTPUT" | grep -E '^[a-f0-9]+@' | head -1 || true)
    
    if [ -n "$NODE_ID" ]; then
        echo "Найдена нода: $NODE_ID"
        break
    fi
    
    if [ $NODE_LIST_COUNT -ge $NODE_LIST_RETRIES ]; then
        echo "Ошибка: Не удалось найти ноду Garage после ${NODE_LIST_RETRIES} попыток"
        echo "Вывод garage node list:"
        echo "$NODE_LIST_OUTPUT"
        exit 1
    fi
    
    sleep 5
done

# --- Проверка cluster layout ---
echo ""
echo "Проверка cluster layout..."

# Проверяем, применён ли layout (не просто существует)
LAYOUT_APPLIED=$(docker exec mytube_garage_local /garage layout list 2>&1 | grep -v '^\[2m' | grep -v '^\[0m' | grep -v '^$' || true)

if echo "$LAYOUT_APPLIED" | grep -q "dc1"; then
    echo "Cluster layout уже применён"
else
    echo "Создание cluster layout..."
    
    if [ -n "$NODE_ID" ]; then
        docker exec mytube_garage_local /garage layout assign -z dc1 -c 1G "$NODE_ID"
        docker exec mytube_garage_local /garage layout apply --version 1
        echo "Cluster layout применён"
    else
        echo "Предупреждение: Не удалось получить ID ноды"
        exit 1
    fi
fi

# --- Ожидание готовности S3 API после layout ---
echo ""
echo "Ожидание готовности S3 API после layout..."

S3_READY_RETRIES=30
S3_READY_COUNT=0

while true; do
    S3_READY_COUNT=$((S3_READY_COUNT + 1))
    echo "Проверка S3 API: попытка $S3_READY_COUNT/$S3_READY_RETRIES..."
    
    if nc -z -w2 $GARAGE_HOST 3900 2>/dev/null; then
        echo "S3 API готов!"
        break
    fi
    
    if [ $S3_READY_COUNT -ge $S3_READY_RETRIES ]; then
        echo "Ошибка: S3 API не готов после ${S3_READY_RETRIES} попыток"
        exit 1
    fi
    
    sleep 5
done

# --- Функция retry для S3 операций ---
s3_retry() {
    local cmd="$1"
    local desc="$2"
    local max_retries=30
    local retry_count=0
    
    while true; do
        retry_count=$((retry_count + 1))
        if [ $retry_count -ge $max_retries ]; then
            echo "Ошибка: Не удалось $desc после ${max_retries} попыток"
            return 1
        fi
        echo "$desc: попытка $retry_count/$max_retries..."
        if eval "$cmd" 2>&1; then
            echo "$desc — успешно"
            return 0
        fi
        sleep 5
    done
}

# --- Проверка bucket ---
echo ""
echo "Проверка бакета '$MINIO_BUCKET'..."

BUCKET_LIST=$(docker exec mytube_garage_local /garage bucket list 2>&1 | grep -v '^\[2m' | grep -v '^\[0m')
if echo "$BUCKET_LIST" | grep -q "$MINIO_BUCKET"; then
    echo "Бакет '$MINIO_BUCKET' уже существует"
else
    echo "Создание бакета '$MINIO_BUCKET'..."
    s3_retry "docker exec mytube_garage_local /garage bucket create $MINIO_BUCKET" "Создание бакета" || exit 1
fi

# --- Проверка key ---
echo ""
echo "Проверка API key '$MINIO_ROOT_USER'..."

KEY_LIST=$(docker exec mytube_garage_local /garage key list 2>&1 | grep -v '^\[2m' | grep -v '^\[0m')
if echo "$KEY_LIST" | grep -q "$MINIO_ROOT_USER"; then
    echo "API key '$MINIO_ROOT_USER' уже существует"
else
    echo "Создание API key '$MINIO_ROOT_USER'..."
    # Создаём key и сохраняем credentials
    KEY_OUTPUT=$(docker exec mytube_garage_local /garage key create $MINIO_ROOT_USER 2>&1)
    echo "$KEY_OUTPUT"
    
    # Парсим access_key и secret_key из вывода
    ACCESS_KEY=$(echo "$KEY_OUTPUT" | grep "Key ID:" | awk '{print $3}')
    SECRET_KEY=$(echo "$KEY_OUTPUT" | grep "Secret key:" | awk '{print $3}')
    
    if [ -n "$ACCESS_KEY" ] && [ -n "$SECRET_KEY" ]; then
        echo "Key создан:"
        echo "  Access Key: $ACCESS_KEY"
        echo "  Secret Key: $SECRET_KEY"
        
        # Сохраняем credentials в файл
        echo "ACCESS_KEY=$ACCESS_KEY" > /tmp/garage_credentials.env
        echo "SECRET_KEY=$SECRET_KEY" >> /tmp/garage_credentials.env
        
        # Копируем credentials в shared volume (если есть)
        if [ -d "/credentials" ]; then
            cp /tmp/garage_credentials.env /credentials/garage_credentials.env
            echo "Credentials сохранены в /credentials/garage_credentials.env"
        fi
    else
        echo "Предупреждение: Не удалось распарсить credentials из вывода"
    fi
fi

# --- Предоставление доступа key к bucket ---
echo ""
echo "Предоставление доступа key к bucket..."

BUCKET_INFO=$(docker exec mytube_garage_local /garage bucket info "$MINIO_BUCKET" 2>&1 | grep -v '^\[2m' | grep -v '^\[0m')
if echo "$BUCKET_INFO" | grep -q "$MINIO_ROOT_USER"; then
    echo "Доступ уже предоставлен"
else
    echo "Предоставление доступа..."
    s3_retry "docker exec mytube_garage_local /garage bucket allow --read --write --owner $MINIO_BUCKET --key $MINIO_ROOT_USER" "Предоставление доступа" || exit 1
fi

echo ""
echo "============================================"
echo "  Garage инициализирован успешно!"
echo "============================================"
