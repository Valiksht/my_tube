"""Фабрика для выбора хранилища.

Возвращает MinIO или файловое хранилище в зависимости от STORAGE_TYPE.
Все сервисы используют эту функцию вместо прямого импорта.
"""

import os

from app.storage.base import BaseStorage


def get_storage() -> BaseStorage:
    """Получить экземпляр хранилища.
    
    Returns:
        Экземпляр BaseStorage (MinIO или filesystem).
    """
    storage_type = os.getenv("STORAGE_TYPE", "minio").lower()
    
    if storage_type == "filesystem":
        from app.storage.filesystem import file_storage
        return file_storage
    else:
        from app.storage.minio import storage
        return storage
