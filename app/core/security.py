"""Безопасность: хеширование паролей и JWT токены.

Использует bcrypt для хеширования паролей и python-jose для JWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# Контекст для хеширования паролей bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хешировать пароль с помощью bcrypt.
    
    Args:
        password: Пароль в открытом виде.
        
    Returns:
        Строка с хешем пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль против хеша.
    
    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хеш пароля из базы данных.
        
    Returns:
        True если пароль совпадает.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Создать JWT access токен.
    
    Используется для API аутентификации (не для браузерных сессий).
    
    Args:
        data: Данные для кодирования (например, user_id, role).
        expires_delta: Время жизни токена. По умолчанию 30 минут.
        
    Returns:
        Закодированный JWT токен.
    """
    settings = get_settings()
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Декодировать и проверить JWT токен.
    
    Args:
        token: JWT токен для проверки.
        
    Returns:
        Данные из токена или None если токен невалиден.
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]
