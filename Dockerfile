FROM python:3.12-slim

# Установка системных зависимостей для ffmpeg и других утилит
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' mytube

# Установка pip в пользовательском окружении
ENV PIP_HOME=/home/mytube/.local/lib/python3.12/site-packages
ENV PYTHONUSERBASE=/home/mytube/.local/lib/python3.12/site-packages
RUN python -m ensurepip --upgrade

WORKDIR /app

# Копирование requirements.txt для кэширования зависимостей
COPY requirements.txt .

# Установка Python-зависимостей в пользовательском окружении
RUN python -m pip install --user -r requirements.txt \
    && rm requirements.txt

# Копирование всех файлов проекта
COPY . .

# Переключение на безопасного пользователя
USER mytube

# Экспорт переменных окружения Python
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Порт для uvicorn
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
