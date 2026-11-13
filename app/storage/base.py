"""Базовый класс объектного хранилища.

Абстракция для работы с MinIO, AWS S3 или другим хранилищем.
Все сервисы работают через этот интерфейс, а не напрямую с MinIO.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    """Абстрактный класс объектного хранилища."""
    
    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        size: int = 0,
    ) -> str:
        """Загрузить файл в хранилище.
        
        Args:
            file: Файловый объект для чтения.
            object_name: Уникальное имя объекта в хранилище.
            content_type: MIME тип файла.
            size: Размер файла в байтах.
            
        Returns:
            URL объекта в хранилище.
        """
        ...
    
    @abstractmethod
    async def get_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Получить URL объекта.
        
        Для публичных видео — постоянная ссылка.
        Для приватных — временная подписанная ссылка.
        
        Args:
            object_name: Имя объекта.
            expires: Время жизни временной ссылки в секундах.
            
        Returns:
            URL для доступа к объекту.
        """
        ...
    
    @abstractmethod
    async def delete(self, object_name: str) -> bool:
        """Удалить объект из хранилища.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            True если объект удалён, False если не найден.
        """
        ...
    
    @abstractmethod
    async def exists(self, object_name: str) -> bool:
        """Проверить существование объекта.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            True если объект существует.
        """
        ...
    
    @abstractmethod
    async def get_content_type(self, object_name: str) -> str:
        """Получить MIME тип объекта.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            MIME тип файла.
        """
        ...
    
    @abstractmethod
    async def get_range(
        self,
        object_name: str,
        start: int,
        end: int,
        content_type: str = "application/octet-stream",
    ) -> BinaryIO:
        """Получить диапазон байтов объекта.
        
        Используется для HTTP Range-запросов (потоковое воспроизведение).
        
        Args:
            object_name: Имя объекта.
            start: Начальный байт (включительно).
            end: Конечный байт (включительно).
            content_type: MIME тип файла.
            
        Returns:
            Файловый объект с байтами диапазона.
        """
        ...
    
    async def _get_file_size(self, object_name: str) -> int:
        """Получить размер объекта в байтах.
        
        Args:
            object_name: Имя объекта.
            
        Returns:
            Размер в байтах.
        """
        raise NotImplementedError
