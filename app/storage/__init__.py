"""Объектное хранилище видео и файлов.

Абстракция для S3-совместимого (MinIO/Garage) или файлового хранилища.
Автоматически выбирает хранилище на основе переменных окружения.
"""

import os

from app.storage.base import BaseStorage
from app.storage.minio import MinIOStorage
from app.storage.filesystem import FileStorage


def get_storage() -> BaseStorage:
    """Получить экземпляр хранилища.
    
    Выбирает S3-совместимое (Garage/MinIO) если доступен, иначе файловое хранилище.
    """
    storage_type = os.getenv("STORAGE_TYPE", "garage").lower()
    
    if storage_type == "filesystem":
        return FileStorage()
    
    # Пробуем S3-совместимое хранилище (Garage/MinIO)
    try:
        return MinIOStorage()
    except Exception:
        # Если S3-хранилище недоступен, используем файловое хранилище
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
