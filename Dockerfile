FROM python:3.13-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Копируем entrypoint-скрипт
COPY scripts/docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh

# Создаём пользователя
RUN useradd -m appuser
USER appuser

# Открываем порт
EXPOSE 8000

# Запуск через entrypoint-скрипт
ENTRYPOINT ["/docker_entrypoint.sh"]
