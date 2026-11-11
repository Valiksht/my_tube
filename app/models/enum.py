__all__ = [
    "UserRole",
    "VideoPrivacy", 
    "CommentStatus",
    "VideoStatus",
    "LikeStatus"
]
"""Единственные определения Enum для всех моделей приложения.

Этот файл содержит все Python-Enum классы, которые используются в SQLAlchemy моделях.
Эти Enum существуют только в памяти Python и не создают нативных типов PostgreSQL ENUM.
Это предпочтительный подход - Enum управляется Python, а String field хранит значения.

## Иерархия Enum (для понимания архитектуры):

UserRole        ──► Роли пользователей: USER, MODERATOR, ADMIN
VideoPrivacy    ──► Типы приватности видео: PUBLIC, UNLISTED, PRIVATE

## Комментарии к Enum:

UserRole - определяет роли в системе: обычный пользователь, модератор, администратор
VideoPrivacy - типы приватности видео: публичное, private, unlisted (как в YouTube)
CommentStatus - статусы модерации комментариев: pending, approved, rejected
VideoStatus - статусы обработки видео: uploaded, processing, ready, failed
LikeStatus - статус лайка: liked/unliked (лайк или его отсутствие)
"""

from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе YouTube Clone.
    
    Ролевая модель:
    ├── USER      ──► Обычный пользователь (может загружать видео, писать комментарии)
    ├── MODERATOR ──► Модератор (может удалять видео и комментарии, отправлять жалобы)
    └── ADMIN     ──► Администратор (полные права управления системой)
    
    Используется в поле User.role.
    """
    
    USER = "user"          # Обычный пользователь
    MODERATOR = "moderator"  # Модератор системы
    ADMIN = "admin"        # Администратор платформы

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum в качестве списка строк.
        
        Returns:
            ["user", "moderator", "admin"]
        """
        return [item.value for item in cls]


class VideoPrivacy(str, Enum):
    """Типы приватности видео для YouTube Clone.
    
    Модель приватности (аналог YouTube):
    ├── PUBLIC      ──► Публичное видео доступно всем
    ├── UNLISTED   ──► Видео не в каталоге, но доступно по ссылке
    └── PRIVATE     ──► Доступно только владельцу и разрешённым пользователям
    
    Используется в поле Video.privacy.
    """
    
    PUBLIC = "public"       # Публичное видео доступно всем
    UNLISTED = "unlisted"   # Видео не в каталоге, но доступно по ссылке
    PRIVATE = "private"     # Доступно только владельцу и разрешённым пользователям

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum в качестве списка строк.
        
        Returns:
            ["public", "unlisted", "private"]
        """
        return [item.value for item in cls]


class CommentStatus(str, Enum):
    """Статусы комментариев для модерации."""
    
    PENDING = "pending"         # Коммент на модерации
    APPROVED = "approved"       # Утвержденный комментарий
    REJECTED = "rejected"       # Отклоненный комментарий

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum."""
        return [item.value for item in cls]


class VideoStatus(str, Enum):
    """Статусы обработки видео."""
    
    UPLOADED = "uploaded"       # Видео загружено
    PROCESSING = "processing"   # Обработка в процессе
    READY = "ready"            # Готово для воспроизведения
    FAILED = "failed"          # Обработка завершилась ошибкой

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum."""
        return [item.value for item in cls]


class LikeStatus(str, Enum):
    """Статусы лайков."""
    
    LIKED = "liked"            # Пользователь поставил лайк
    UNLIKED = "unliked"        # Пользователь снял лайк или ещё не ставил

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum."""
        return [item.value for item in cls]