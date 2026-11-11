"""Общие исключения и ошибки приложения.

Централизованное управление ошибками для единообразных HTTP-ответов.
"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое приложение исключение.
    
    Используется для создания специфичных исключений с HTTP статусами.
    """
    
    def __init__(
        self,
        detail: str = "Internal server error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: dict | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


class NotFoundException(AppException):
    """Ресурс не найден (404)."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AuthenticationRequiredException(AppException):
    """Пользователь не авторизован (401)."""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class PermissionDeniedException(AppException):
    """Недостаточно прав (403)."""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class DuplicateResourceException(AppException):
    """Ресурс уже существует (409)."""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationException(AppException):
    """Ошибка валидации данных (422)."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class VideoProcessingException(AppException):
    """Ошибка обработки видео."""
    
    def __init__(self, detail: str = "Video processing failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


__all__ = [
    "AppException",
    "NotFoundException",
    "AuthenticationRequiredException",
    "PermissionDeniedException",
    "DuplicateResourceException",
    "ValidationException",
    "VideoProcessingException",
]
