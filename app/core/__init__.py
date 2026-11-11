"""Core модуль приложения.

Содержит конфигурацию, безопасность и общие настройки.
"""

from app.core.config import get_settings, Settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.csrf import (
    generate_csrf_token,
    verify_csrf_token,
    set_csrf_cookie,
)
from app.core.exceptions import (
    AppException,
    NotFoundException,
    AuthenticationRequiredException,
    PermissionDeniedException,
    DuplicateResourceException,
    ValidationException,
    VideoProcessingException,
)

__all__ = [
    # Config
    "get_settings",
    "Settings",
    
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    
    # CSRF
    "generate_csrf_token",
    "verify_csrf_token",
    "set_csrf_cookie",
    
    # Exceptions
    "AppException",
    "NotFoundException",
    "AuthenticationRequiredException",
    "PermissionDeniedException",
    "DuplicateResourceException",
    "ValidationException",
    "VideoProcessingException",
]
