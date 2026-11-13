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
        self.base_url = settings.storage_base_url
    
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
        """Определить MIME-тип файла по его расширению."""
        import mimetypes
        content_type, _ = mimetypes.guess_type(object_name)
        return content_type or "application/octet-stream"
    
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
    
    async def get_range(
        self,
        object_name: str,
        start: int,
        end: int,
        content_type: str = "application/octet-stream",
    ) -> BinaryIO:
        """Получить диапазон байтов файла."""
        file_path = self.storage_dir / object_name
        
        def iter_bytes():
            with open(file_path, "rb") as f:
                f.seek(start)
                length = end - start + 1
                bytes_read = 0
                while bytes_read < length:
                    chunk_size = min(64 * 1024, length - bytes_read)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    yield chunk
        
        return iter_bytes()
    
    async def _get_file_size(self, object_name: str) -> int:
        """Получить размер файла в байтах."""
        file_path = self.storage_dir / object_name
        return file_path.stat().st_size


# Глобальный экземпляр
file_storage = FileStorage()
