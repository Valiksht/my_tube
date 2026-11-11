"""Объектное хранилище видео и файлов.

Абстракция для MinIO/S3. Сервисы используют этот интерфейс,
а не работают напрямую с MinIO.
"""

from app.storage.base import BaseStorage
from app.storage.minio import storage, MinIOStorage

__all__ = [
    "BaseStorage",
    "storage",
    "MinIOStorage",
]
