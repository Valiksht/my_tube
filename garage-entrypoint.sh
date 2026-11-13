#!/bin/sh
# Entrypoint для Garage v2.2.0
# Автоматически создаёт bucket через S3 API после запуска сервера

set -e

echo "============================================"
echo "  Запуск Garage с инициализацией bucket"
echo "============================================"

# Запускаем Garage в фоне
/garage server &
GARAGE_PID=$!

echo "Garage запущен с PID $GARAGE_PID"

# --- Ожидание готовности S3 API (порт 3900) ---
echo "Ожидание готовности Garage S3 API..."

MAX_RETRIES=60
RETRY_COUNT=0

while ! nc -z -w2 localhost 3900 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Ошибка: Не удалось подождать Garage S3 API после ${MAX_RETRIES} попыток"
        kill $GARAGE_PID
        exit 1
    fi
    
    sleep 2
done

echo "Garage S3 API доступен!"

# --- Ожидание готовности RPC (порт 3901) ---
echo "Ожидание готовности Garage RPC..."

RPC_RETRY_COUNT=0
RPC_MAX_RETRIES=60

while ! nc -z -w2 localhost 3901 2>/dev/null; do
    RPC_RETRY_COUNT=$((RPC_RETRY_COUNT + 1))
    
    if [ $RPC_RETRY_COUNT -ge $RPC_MAX_RETRIES ]; then
        echo "Ошибка: Не удалось подождать Garage RPC после ${RPC_MAX_RETRIES} попыток"
        kill $GARAGE_PID
        exit 1
    fi
    
    sleep 2
done

echo "Garage RPC готов!"

# --- Создание cluster layout ---
echo ""
echo "Создание cluster layout..."

# Проверяем, есть ли уже назначенные узлы
if /garage node list 2>/dev/null | grep -q .; then
    echo "Cluster layout уже настроен"
else
    # Получаем ID ноды
    NODE_ID=$(/garage node id 2>/dev/null || true)

    if [ -n "$NODE_ID" ]; then
        echo "ID ноды: $NODE_ID"
        /garage layout assign -z dc1 -c 1G "$NODE_ID"
        /garage layout apply --version 1
        echo "Cluster layout применён"
    else
        echo "Ошибка: Не удалось получить ID ноды"
        kill $GARAGE_PID
        exit 1
    fi
fi

# --- Ожидание готовности S3 API после layout ---
echo ""
echo "Ожидание готовности S3 API после layout..."

S3_RETRY_COUNT=0
S3_MAX_RETRIES=30

while true; do
    S3_RETRY_COUNT=$((S3_RETRY_COUNT + 1))
    
    if nc -z -w2 localhost 3900 2>/dev/null; then
        echo "S3 API готов!"
        break
    fi
    
    if [ $S3_RETRY_COUNT -ge $S3_MAX_RETRIES ]; then
        echo "Ошибка: S3 API не готов после ${S3_MAX_RETRIES} попыток"
        kill $GARAGE_PID
        exit 1
    fi
    
    sleep 3
done

# --- Создание API key через Garage CLI ---
KEY_NAME="${GARAGE_DEFAULT_KEY_NAME:-mytube-key}"
echo ""
echo "Проверка API key '$KEY_NAME'..."

if /garage key list 2>&1 | grep -q "$KEY_NAME"; then
    echo "API key '$KEY_NAME' уже существует"
else
    echo "Создание API key '$KEY_NAME'..."
    KEY_OUTPUT=$(/garage key create "$KEY_NAME" 2>&1)
    echo "$KEY_OUTPUT"
fi

# --- Предоставление доступа key к bucket ---
BUCKET="${GARAGE_DEFAULT_BUCKET:-videos}"
echo ""
echo "Проверка бакета '$BUCKET'..."

if /garage bucket list 2>&1 | grep -q "$BUCKET"; then
    echo "Бакет '$BUCKET' уже существует"
else
    echo "Создание бакета '$BUCKET'..."
    /garage bucket create "$BUCKET"
    echo "Бакет создан"
fi

echo ""
echo "Предоставление доступа key к bucket..."

if /garage bucket info "$BUCKET" 2>&1 | grep -q "$KEY_NAME"; then
    echo "Доступ уже предоставлен"
else
    echo "Предоставление доступа..."
    /garage bucket allow --read --write --owner "$BUCKET" --key "$KEY_NAME"
    echo "Доступ предоставлен"
fi

# --- Получение credentials созданного key ---
echo ""
echo "Получение credentials key '$KEY_NAME'..."

KEY_INFO=$(/garage key info "$KEY_NAME" 2>&1)
echo "$KEY_INFO"

# Парсим credentials из вывода
ACCESS_KEY=$(echo "$KEY_INFO" | grep "Key ID:" | awk '{print $3}')
SECRET_KEY=$(echo "$KEY_INFO" | grep "Secret key:" | awk '{print $3}')

if [ -n "$ACCESS_KEY" ] && [ -n "$SECRET_KEY" ]; then
    echo ""
    echo "============================================"
    echo "  Credentials для S3 API:"
    echo "  Access Key: $ACCESS_KEY"
    echo "  Secret Key: $SECRET_KEY"
    echo "  Bucket: $BUCKET"
    echo "============================================"
    
    # Сохраняем credentials в файл
    mkdir -p /etc/garage
    echo "GARAGE_S3_ACCESS_KEY=$ACCESS_KEY" > /etc/garage/s3_credentials.env
    echo "GARAGE_S3_SECRET_KEY=$SECRET_KEY" >> /etc/garage/s3_credentials.env
    
    # Копируем credentials в shared volume для доступа извне
    if [ -d "/credentials" ]; then
        cp /etc/garage/s3_credentials.env /credentials/garage_credentials.env
        echo "Credentials сохранены в /credentials/garage_credentials.env"
    fi
else
    echo ""
    echo "Предупреждение: Не удалось получить credentials"
fi

# --- Ожидание сигнала остановки ---
echo ""
echo "Garage запущен и инициализирован. Ожидание процессов..."

# Перехват сигнала остановки
catch_signal() {
    echo "Получен сигнал, останавливаю Garage..."
    kill $GARAGE_PID
    wait $GARAGE_PID
    echo "Garage остановлен"
    exit 0
}

trap catch_signal SIGTERM SIGINT

# Ждём Garage
wait $GARAGE_PID
