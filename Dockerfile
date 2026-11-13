
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpq5 \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY . .

COPY scripts/docker_entrypoint.sh /docker_entrypoint.sh

RUN chmod +x /docker_entrypoint.sh

# Permissions and storage directory
RUN useradd -m -s /bin/bash appuser \
    && mkdir -p /app/storage \
    && chown -R appuser:appuser /app \
    && chmod +x /docker_entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/docker_entrypoint.sh"]
