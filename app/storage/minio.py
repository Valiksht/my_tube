"""Реализация объектного хранилища на базе S3-совместимого API.

Использует minio Python SDK для работы с MinIO, Garage или другим
S3-совместимым хранилищем.
"""

import os
import uuid
from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.storage.base import BaseStorage
from app.core.config import get_settings


class MinIOStorage(BaseStorage):
    """Хранилище на базе MinIO/S3/Garage.
    
    Поддерживает публичные и приватные бакеты.
    Для приватных объектов генерирует временные подписанные ссылки.
    Работает с любым S3-совместимым хранилищем.
    """
    
    def __init__(
        self,
        client: Minio | None = None,
        bucket: str | None = None,
    ):
        settings = get_settings()
        
        # Поддержка переменных окружения для Garage (S3-совместимый API)
        s3_host = os.getenv("GARAGE_HOST") or os.getenv("MINIO_HOST", "localhost")
        s3_port = os.getenv("GARAGE_S3_PORT") or os.getenv("MINIO_PORT", "3900")
        s3_region = os.getenv("GARAGE_S3_REGION") or os.getenv("MINIO_REGION", "garage")
        s3_public_url = os.getenv("GARAGE_S3_PUBLIC_URL") or os.getenv("MINIO_PUBLIC_URL", "http://localhost:3900")
        s3_secure = os.getenv("GARAGE_S3_SECURE") or os.getenv("MINIO_SECURE", "false")
        
        # Читаем credentials из переменных окружения или из файла
        s3_access = os.getenv("GARAGE_S3_ACCESS_KEY")
        s3_secret = os.getenv("GARAGE_S3_SECRET_KEY")
        
        # Если credentials не заданы, пробуем прочитать из файла
        if not s3_access or not s3_secret:
            cred_file = os.getenv("GARAGE_CREDENTIALS_FILE", "/garage_credentials/garage_credentials.env")
            if os.path.exists(cred_file):
                with open(cred_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GARAGE_S3_ACCESS_KEY="):
                            s3_access = line.split("=", 1)[1]
                        elif line.startswith("GARAGE_S3_SECRET_KEY="):
                            s3_secret = line.split("=", 1)[1]
        
        # Fallback на значения по умолчанию
        if not s3_access:
            s3_access = os.getenv("MINIO_ROOT_USER", "garageadmin")
        if not s3_secret:
            s3_secret = os.getenv("MINIO_ROOT_PASSWORD", "garageadmin123")
        
        self.client = client or Minio(
            f"{s3_host}:{s3_port}",
            access_key=s3_access,
            secret_key=s3_secret,
            secure=s3_secure.lower() == "true",
            region=s3_region,
        )
        
        self.bucket = bucket or os.getenv("GARAGE_BUCKET") or os.getenv("MINIO_BUCKET", "videos")
        self.public_url = s3_public_url
    
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
        
        # Garage автоматически создаёт бакет при первом запросе.
        # MinIO SDK v7.x имеет баг: bucket_exists использует регион
        # us-east-1 для подписи, а Garage ожидает свой регион.
        # Поэтому проверку existence пропускаем — Garage создаст бакет сам.
        
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
                expires=timedelta(seconds=expires),
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
    
    async def get_range(
        self,
        object_name: str,
        start: int,
        end: int,
        content_type: str = "application/octet-stream",
    ) -> BinaryIO:
        """Получить диапазон байтов объекта.
        
        Args:
            object_name: Имя объекта.
            start: Начальный байт (включительно).
            end: Конечный байт (включительно).
            content_type: MIME тип файла.
            
        Returns:
            Файловый объект с байтами диапазона.
        """
        # MinIO SDK: offset — с какого байта начать,
        # length — сколько байт прочитать.
        length = end - start + 1
        
        return self.client.get_object(
            bucket_name=self.bucket,
            object_name=object_name,
            offset=start,
            length=length,
        )
    
    async def _get_file_size(self, object_name: str) -> int:
        """Получить размер объекта в байтах.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            Размер в байтах.
        """
        stat = self.client.stat_object(
            bucket_name=self.bucket,
            object_name=object_name,
        )
        return stat.size
    
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
