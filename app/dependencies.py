"""Зависимости FastAPI.

Получение сессии БД, текущего пользователя, проверка ролей.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationRequiredException,
    PermissionDeniedException,
)
from app.database.dependencies import get_db
from app.models.users import User
from app.models.session import UserSession
from app.core.config import get_settings
from sqlalchemy import select


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Получить текущего авторизованного пользователя.
    
    Проверяет session_id из Cookie и возвращает пользователя.
    
    Args:
        request: FastAPI Request.
        db: Сессия базы данных.
        
    Returns:
        Текущий пользователь.
        
    Raises:
        HTTPException 401: Если пользователь не авторизован.
    """
    settings = get_settings()
    
    session_id = request.cookies.get(settings.session_cookie)
    if not session_id:
        raise AuthenticationRequiredException()
    
    query = (
        select(UserSession)
        .where(
            UserSession.session_id == session_id,
            UserSession.is_active == "1",
            UserSession.expires_at > __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ),
        )
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AuthenticationRequiredException("Session expired or invalid")
    
    return session.user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Получить текущего пользователя (необязательно).
    
    Если пользователь авторизован — возвращает его.
    Если нет — возвращает None.
    
    Args:
        request: FastAPI Request.
        db: Сессия базы данных.
        
    Returns:
        Пользователь или None.
    """
    settings = get_settings()
    
    session_id = request.cookies.get(settings.session_cookie)
    if not session_id:
        return None
    
    query = (
        select(UserSession)
        .where(
            UserSession.session_id == session_id,
            UserSession.is_active == "1",
            UserSession.expires_at > __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ),
        )
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        return None
    
    return session.user


def require_role(*roles: str):
    """Зависимость для проверки роли пользователя.
    
    Args:
        *roles: Список допустимых ролей.
        
    Returns:
        Функция-зависимость для FastAPI.
    """
    async def _check_role(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDeniedException(
                f"Role '{user.role}' does not have permission"
            )
        return user
    return _check_role


def require_moderator_or_admin():
    """Зависимость для модератора или администратора."""
    return require_role("moderator", "admin")


def require_admin():
    """Зависимость для администратора."""
    return require_role("admin")


__all__ = [
    "get_current_user",
    "get_optional_user",
    "require_role",
    "require_moderator_or_admin",
    "require_admin",
    "get_db",
]
