"""CSRF защита для форм и изменяющих состояние запросов.

Использует двойной cookie validation pattern:
1. CSRF токен хранится в HttpOnly Cookie
2. Токен отправляется в заголовке X-CSRF-Token
3. Сервер сравнивает оба значения
"""

import secrets
from functools import wraps
from typing import Callable

from fastapi import Request, HTTPException, status
from fastapi.responses import Response

from app.core.config import get_settings


def generate_csrf_token() -> str:
    """Сгенерировать криптографически случайный CSRF токен.
    
    Returns:
        Случайная строка длиной 32 байта (URL-safe base64).
    """
    return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> str:
    """Получить CSRF токен из Cookie или заголовка.
    
    Args:
        request: FastAPI Request объект.
        
    Returns:
        CSRF токен.
        
    Raises:
        HTTPException: 403 если токен не найден.
    """
    settings = get_settings()
    
    # Сначала проверяем Cookie
    cookie_token = request.cookies.get(settings.session_cookie + "_csrf")
    if cookie_token:
        return cookie_token
    
    # Затем проверяем заголовок
    header_token = request.headers.get("X-CSRF-Token")
    if header_token:
        return header_token
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="CSRF token not found",
    )


def verify_csrf_token(request: Request) -> bool:
    """Проверить CSRF токен.
    
    Сравнивает токен из Cookie с токеном из заголовка.
    
    Args:
        request: FastAPI Request объект.
        
    Returns:
        True если токен валиден.
        
    Raises:
        HTTPException: 403 если токен невалиден.
    """
    settings = get_settings()
    
    cookie_token = request.cookies.get(settings.session_cookie + "_csrf")
    header_token = request.headers.get("X-CSRF-Token")
    
    if not cookie_token or not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )
    
    if not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )
    
    return True


def csrf_protect(func: Callable) -> Callable:
    """Декоратор для CSRF защиты обработчиков.
    
    Используется для функций-обработчиков HTML форм.
    Для FastAPI зависимостей лучше использовать verify_csrf_token напрямую.
    
    Example:
        @app.post("/upload", methods=["POST"])
        @csrf_protect
        async def handle_upload(request: Request):
            ...
    """
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        verify_csrf_token(request)
        return await func(*args, request=request, **kwargs)
    return wrapper


def set_csrf_cookie(response: Response) -> Response:
    """Установить CSRF Cookie при успешной авторизации.
    
    Args:
        response: FastAPI Response объект.
        
    Returns:
        Response с установленным CSRF Cookie.
    """
    settings = get_settings()
    token = generate_csrf_token()
    
    response.set_cookie(
        cookie_name=settings.session_cookie + "_csrf",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
    )
    
    return response


__all__ = [
    "generate_csrf_token",
    "get_csrf_token",
    "verify_csrf_token",
    "csrf_protect",
    "set_csrf_cookie",
]
