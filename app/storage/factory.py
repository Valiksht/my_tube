"""Фабрика для выбора хранилища.

Возвращает S3-совместимое (MinIO/Garage) или файловое хранилище
в зависимости от STORAGE_TYPE.
Все сервисы используют эту функцию вместо прямого импорта.
"""

import os

from app.core.config import get_settings
from app.storage.base import BaseStorage


def get_storage() -> BaseStorage:
    settings = get_settings()

    storage_type = os.getenv(
        "STORAGE_TYPE",
        settings.storage_type,
    ).lower()

    if storage_type == "filesystem":
        from app.storage.filesystem import file_storage
        return file_storage

    if storage_type in ("garage", "minio", "s3"):
        from app.storage.minio import storage
        return storage

    raise ValueError(
        f"Unsupported storage type: {storage_type}"
    )
