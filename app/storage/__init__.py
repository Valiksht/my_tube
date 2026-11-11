"""Объектное хранилище видео и файлов.

Абстракция для MinIO/S3 или файлового хранилища.
Автоматически выбирает хранилище на основе переменных окружения.
"""

import os

from app.storage.base import BaseStorage
from app.storage.minio import MinIOStorage
from app.storage.filesystem import FileStorage


def get_storage() -> BaseStorage:
    """Получить экземпляр хранилища.
    
    Выбирает MinIO если доступен, иначе файловое хранилище.
    """
    storage_type = os.getenv("STORAGE_TYPE", "minio").lower()
    
    if storage_type == "filesystem":
        return FileStorage()
    
    # Пробуем MinIO
    try:
        return MinIOStorage()
    except Exception:
        # Если MinIO недоступен, используем файловое хранилище
        return FileStorage()


# Глобальный экземпляр хранилища
storage = get_storage()

__all__ = [
    "BaseStorage",
    "storage",
    "MinIOStorage",
    "FileStorage",
    "get_storage",
]
