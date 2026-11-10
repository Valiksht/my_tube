"""Перечисления для моделей приложения."""

from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе."""

    USER = "user"               # Обычный пользователь
    MODERATOR = "moderator"     # Модератор
    ADMIN = "admin"             # Администратор

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum."""
        return [item.value for item in cls]


class VideoPrivacy(str, Enum):
    """Типы приватности видео."""

    PUBLIC = "public"           # Публичное видео для всех
    UNLISTED = "unlisted"       # Не добавлено в каталог
    PRIVATE = "private"         # Доступно только для авторизованных пользователей

    @classmethod
    def values(cls) -> list[str]:
        """Получить все значения Enum."""
        return [item.value for item in cls]


class CommentStatus(str, Enum):
    """Статусы комментариев."""

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


# Экспорт всех перечислений для использования в других модулях
__all__ = [
    "UserRole",
    "VideoPrivacy",
    "CommentStatus",
    "VideoStatus",
    "LikeStatus"
]
