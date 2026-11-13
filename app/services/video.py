"""Сервисы для работы с видео.

Бизнес-логика: создание, обновление, проверка доступа, просмотр,
загрузка файлов в объектное хранилище.
"""

import os
import tempfile
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.video import Video
from app.models.channel import Channel
from app.models.enum import VideoPrivacy
from app.crud.video import video_repo
from app.crud.channel import channel_repo
from app.schemas.video import VideoCreate, VideoUpdate
from app.storage.base import BaseStorage


class VideoService:
    """Сервис для работы с видео."""
    
    def __init__(
        self,
        db: AsyncSession,
        storage: BaseStorage | None = None,
    ):
        self.db = db
        if storage is not None:
            self.storage = storage
        else:
            from app.storage.factory import get_storage
            self.storage = get_storage()
    
    async def create_video(
        self,
        channel_id: int,
        title: str,
        description: str = "",
        privacy: str = "public",
    ) -> Video:
        """Создать новое видео.
        
        Args:
            channel_id: ID канала владельца.
            title: Название видео.
            description: Описание.
            privacy: Тип приватности.
            
        Returns:
            Созданное видео.
        """
        # Проверяем что канал существует
        channel = await channel_repo.get_by_id(self.db, channel_id)
        if not channel:
            raise ValueError("Channel not found")
        
        video = await video_repo.create_video(
            self.db,
            channel_id=channel_id,
            title=title,
            description=description,
            privacy=privacy,
        )
        
        return video
    
    async def upload_video_file(
        self,
        video: Video,
        file,
        content_type: str = "video/mp4",
        size: int = 0,
    ) -> Video:
        """Загрузить видео файл в хранилище.
        
        Args:
            video: Видео объект.
            file: Файловый объект.
            content_type: MIME тип файла.
            size: Размер файла в байтах.
            
        Returns:
            Обновлённый видео объект.
        """
        if not self.storage:
            raise RuntimeError("Storage not configured")
        
        # Генерируем уникальное имя объекта
        object_name = f"videos/{video.id}{self._get_extension(content_type)}"
        
        # Загружаем файл
        video_url = await self.storage.upload(
            file=file,
            object_name=object_name,
            content_type=content_type,
            size=size,
        )
        
        # Обновляем видео в БД
        video.video_url = video_url
        video.video_object_name = object_name
        await self.db.flush()
        
        return video
    
    async def upload_thumbnail(
        self,
        video: Video,
        file,
        content_type: str = "image/jpeg",
    ) -> Video:
        """Загрузить превью видео.
        
        Args:
            video: Видео объект.
            file: Файловый объект.
            content_type: MIME тип изображения.
            
        Returns:
            Обновлённый видео объект.
        """
        if not self.storage:
            raise RuntimeError("Storage not configured")
        
        object_name = f"thumbnails/{video.id}.jpg"
        thumbnail_url = await self.storage.upload(
            file=file,
            object_name=object_name,
            content_type=content_type,
        )
        
        video.thumbnail_url = thumbnail_url
        video.thumbnail_object_name = object_name
        await self.db.flush()
        
        return video
    
    async def get_video(
        self,
        video_id: int,
        current_user=None,
    ) -> Optional[Video]:
        """Получить видео с проверкой доступа.
        
        Args:
            video_id: ID видео.
            current_user: Текущий пользователь (может быть None).
            
        Returns:
            Видео или None.
        """
        video = await video_repo.get_by_id_with(
            self.db,
            video_id,
            selectinload(Video.channel).selectinload(Channel.user),
        )
        if not video:
            return None
        
        # Проверяем доступ
        if not self._check_access(video, current_user):
            return None
        
        return video
    
    async def get_video_stream_url(
        self,
        video: Video,
        current_user=None,
        expires: int = 3600,
    ) -> Optional[str]:
        """Получить ссылку на поток видео."""

        if not video.video_object_name:
            return None

        if not self._check_access(video, current_user):
            return None

        return await self.storage.get_url(
            video.video_object_name,
            expires=expires,
        )
    
    async def get_user_videos(
        self,
        channel_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Получить видео канала."""
        return await video_repo.get_by_channel(
            self.db,
            channel_id=channel_id,
            skip=skip,
            limit=limit,
        )
    
    async def get_public_videos(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Получить список публичных видео."""
        return await video_repo.get_public_videos(
            self.db,
            skip=skip,
            limit=limit,
        )
    
    async def search_videos(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Video]:
        """Поиск видео по названию."""
        return await video_repo.search_videos(
            self.db,
            query=query,
            skip=skip,
            limit=limit,
        )
    
    async def update_video(
        self,
        video: Video,
        current_user,
        obj_data: VideoUpdate,
    ) -> Video:
        """Обновить видео.
        
        Args:
            video: Видео для обновления.
            current_user: Текущий пользователь.
            obj_data: Новые данные.
            
        Returns:
            Обновлённое видео.
            
        Raises:
            PermissionError: Если у пользователя нет прав.
        """
        # Проверяем что пользователь владелец
        if current_user and video.channel.user.id != current_user.id:
            raise PermissionError("Not enough permissions")
        
        video_dict = obj_data.model_dump(exclude_unset=True)
        video = await video_repo.update(
            self.db,
            video,
            video_dict,
        )
        
        return video
    
    async def delete_video(self, video: Video) -> None:
        """Удалить видео и файлы из хранилища.
        
        Args:
            video: Видео для удаления.
        """
        # Удаляем файлы из хранилища
        if self.storage:
            if video.video_object_name:
                await self.storage.delete(video.video_object_name)
            if video.thumbnail_object_name:
                await self.storage.delete(video.thumbnail_object_name)
        
        await video_repo.remove(self.db, video)
    
    async def increment_view_count(self, video: Video) -> Video:
        """Увеличить счётчик просмотров."""
        return await video_repo.increment_view_count(self.db, video)
    
    def _check_access(
        self,
        video: Video,
        current_user=None,
    ) -> bool:
        """Проверить доступ к видео.
        
        Args:
            video: Видео для проверки.
            current_user: Текущий пользователь.
            
        Returns:
            True если доступ разрешён.
        """
        # Публичное и опубликованное — доступно всем
        if (
            video.privacy == VideoPrivacy.PUBLIC.value
            and video.is_published
        ):
            return True
        
        # Unlisted — доступно всем по ссылке
        if video.privacy == VideoPrivacy.UNLISTED.value:
            return True
        
        # Приватное — только владельцу и авторизованным
        if video.privacy == VideoPrivacy.PRIVATE.value:
            if not current_user:
                return False
            
            # Проверяем что пользователь владелец
            return video.channel.user.id == current_user.id
        
        return False
    
    @staticmethod
    def _get_extension(content_type: str) -> str:
        """Получить расширение файла из MIME типа."""
        mapping = {
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/ogg": ".ogv",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
        }
        return mapping.get(content_type, ".bin")
    
    @staticmethod
    def _extract_object_name(url: str) -> str:
        """Извлечь имя объекта из URL."""

        from urllib.parse import unquote, urlparse
        path = unquote(urlparse(url).path).lstrip("/")
        # URL Garage: /videos/videos/123.mp4
        # URL файлового хранилища: /storage/videos/123.mp4
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "videos":
            return "/".join(parts[1:])
        if len(parts) >= 3 and parts[0] == "storage":
            return "/".join(parts[1:])
        return path

