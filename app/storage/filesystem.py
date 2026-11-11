"""Файловое хранилище как fallback когда MinIO недоступен.

Используется когда MinIO образы недоступны (Docker Hub/Quay проблемы).
"""

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from app.storage.base import BaseStorage
from app.core.config import get_settings


class FileStorage(BaseStorage):
    """Файловое хранилище на локальной дисковой системе.
    
    Fallback решение когда MinIO недоступен.
    Хранит файлы в указанной директории.
    """
    
    def __init__(self, storage_dir: str | None = None):
        settings = get_settings()
        self.storage_dir = Path(storage_dir or settings.storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = os.getenv("STORAGE_BASE_URL", "http://localhost:8000/static/storage")
    
    async def upload(
        self,
        file: BinaryIO,
        object_name: str | None = None,
        content_type: str = "application/octet-stream",
        size: int = 0,
    ) -> str:
        """Загрузить файл в файловое хранилище."""
        if not object_name:
            ext = self._extension_from_content_type(content_type)
            object_name = f"{uuid.uuid4().hex}{ext}"
        
        # Создаём поддиректории
        file_path = self.storage_dir / object_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        file.seek(0)
        with open(file_path, "wb") as f:
            while True:
                chunk = file.read(8192)
                if not chunk:
                    break
                f.write(chunk)
        
        return f"{self.base_url}/{object_name}"
    
    async def get_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Получить URL файла."""
        return f"{self.base_url}/{object_name}"
    
    async def delete(self, object_name: str) -> bool:
        """Удалить файл."""
        file_path = self.storage_dir / object_name
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False
    
    async def exists(self, object_name: str) -> bool:
        """Проверить существование файла."""
        return (self.storage_dir / object_name).exists()
    
    async def get_content_type(self, object_name: str) -> str:
        """Получить MIME тип."""
        return self._extension_from_content_type(object_name)
    
    @staticmethod
    def _extension_from_content_type(content_type: str) -> str:
        """Получить расширение из MIME типа."""
        mapping = {
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/ogg": ".ogv",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
        }
        return mapping.get(content_type, ".bin")


# Глобальный экземпляр
file_storage = FileStorage()
