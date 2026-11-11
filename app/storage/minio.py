"""Реализация объектного хранилища на базе MinIO.

Использует minio Python SDK для работы с S3-совместимым хранилищем.
"""

import os
import uuid
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.storage.base import BaseStorage
from app.core.config import get_settings


class MinIOStorage(BaseStorage):
    """Хранилище на базе MinIO/S3.
    
    Поддерживает публичные и приватные бакеты.
    Для приватных объектов генерирует временные подписанные ссылки.
    """
    
    def __init__(
        self,
        client: Minio | None = None,
        bucket: str | None = None,
    ):
        settings = get_settings()
        
        self.client = client or Minio(
            os.getenv("MINIO_HOST", "localhost"),
            access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )
        
        self.bucket = bucket or os.getenv("MINIO_BUCKET", "videos")
        self.public_url = os.getenv(
            "MINIO_PUBLIC_URL",
            "http://localhost:9000",
        )
    
    async def upload(
        self,
        file: BinaryIO,
        object_name: str | None = None,
        content_type: str = "application/octet-stream",
        size: int = 0,
    ) -> str:
        """Загрузить файл в MinIO.
        
        Args:
            file: Файловый объект для чтения.
            object_name: Имя объекта. Если None — генерируется уникальное.
            content_type: MIME тип файла.
            size: Размер файла в байтах.
            
        Returns:
            URL объекта.
        """
        if not object_name:
            object_name = self._generate_object_name(content_type)
        
        # Проверяем существование бакета
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            # Устанавливаем публичный доступ для бакета
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                    }
                ],
            }
            # self.client.set_bucket_policy(self.bucket, json.dumps(policy))
        
        # Загружаем файл
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file,
            length=size if size > 0 else -1,
            content_type=content_type,
        )
        
        return f"{self.public_url}/{self.bucket}/{object_name}"
    
    async def get_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Получить URL объекта.
        
        Для публичных видео возвращает постоянную ссылку.
        Для приватных — временную подписанную ссылку.
        
        Args:
            object_name: Имя объекта.
            expires: Время жизни ссылки в секундах.
            
        Returns:
            URL для доступа.
        """
        try:
            # Пробуем получить подписанную ссылку
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires,
            )
            return url
        except S3Error:
            return f"{self.public_url}/{self.bucket}/{object_name}"
    
    async def delete(self, object_name: str) -> bool:
        """Удалить объект из MinIO.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            True если удалён, False если не найден.
        """
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error:
            return False
    
    async def exists(self, object_name: str) -> bool:
        """Проверить существование объекта.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            True если существует.
        """
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False
    
    async def get_content_type(self, object_name: str) -> str:
        """Получить MIME тип объекта.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            MIME тип.
        """
        try:
            stat = self.client.stat_object(self.bucket, object_name)
            return stat.content_type or "application/octet-stream"
        except S3Error:
            return "application/octet-stream"
    
    def _generate_object_name(self, content_type: str) -> str:
        """Сгенерировать уникальное имя объекта.
        
        Не использует исходное имя файла — только уникальный UUID.
        
        Args:
            content_type: MIME тип файла.
            
        Returns:
            Уникальное имя объекта.
        """
        ext = self._extension_from_content_type(content_type)
        return f"{uuid.uuid4().hex}{ext}"
    
    @staticmethod
    def _extension_from_content_type(content_type: str) -> str:
        """Получить расширение файла из MIME типа.
        
        Args:
            content_type: MIME тип.
            
        Returns:
            Расширение файла (с точкой).
        """
        mapping = {
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/ogg": ".ogv",
            "video/avi": ".avi",
            "video/mov": ".mov",
            "video/mpeg": ".mpeg",
            "video/x-msvideo": ".avi",
            "video/x-matroska": ".mkv",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return mapping.get(content_type, ".bin")


# Глобальный экземпляр хранилища
storage = MinIOStorage()
