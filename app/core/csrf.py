"""CSRF защита для форм и изменяющих состояние запросов.

Использует двойной cookie validation pattern:
1. CSRF токен хранится в HttpOnly Cookie
2. Токен отправляется в заголовке X-CSRF-Token
3. Сервер сравнивает оба значения
"""

import logging
import secrets

from fastapi import Request, HTTPException, status
from fastapi.responses import Response

from app.core.config import get_settings

logger = logging.getLogger(__name__)


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


async def verify_csrf_token(request: Request, form: dict = None) -> bool:
    """Проверить CSRF токен.
    
    Поддерживает два паттерна:
    1. Double-submit cookie: токен из Cookie сравнивается с токеном из заголовка X-CSRF-Token.
    2. Form field: токен из Cookie сравнивается с токеном из поля формы csrf_token.
    
    Args:
        request: FastAPI Request объект.
        form: Словарь с данными формы (опционально, для паттерна form field).
        
    Returns:
        True если токен валиден.
        
    Raises:
        HTTPException: 403 если токен невалиден.
    """
    settings = get_settings()
    
    cookie_token = request.cookies.get(settings.session_cookie + "_csrf")
    header_token = request.headers.get("X-CSRF-Token")
    
    # Паттерн 1: заголовок X-CSRF-Token (double-submit cookie)
    if cookie_token and header_token:
        if not secrets.compare_digest(cookie_token, header_token):
            logger.warning("CSRF token mismatch (header)")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch",
            )
        return True
    
    # Паттерн 2: поле формы csrf_token
    if form:
        form_token = form.get("csrf_token")
        if form_token and cookie_token:
            if secrets.compare_digest(cookie_token, form_token):
                return True
            logger.warning("CSRF token mismatch (form)")
        elif not cookie_token:
            logger.warning("CSRF cookie not found on request")
        elif not form_token:
            logger.warning(
                "CSRF form token not found. Form keys: %s", list(form.keys())
            )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="CSRF token missing or invalid",
    )


async def csrf_protect_form(request: Request, form: dict = None) -> None:
    """Зависимость FastAPI для CSRF-защиты HTML-форм.
    
    Проверяет CSRF токен из Cookie и поля формы csrf_token.
    Используется как Depends() в обработчиках POST-запросов.
    
    Example:
        @app.post("/register")
        async def register(request: Request, db: AsyncSession = Depends(get_db),
                           _csrf: None = Depends(csrf_protect_form)):
            ...
    """
    await verify_csrf_token(request, form=form)


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
        key=settings.session_cookie + "_csrf",
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
    "csrf_protect_form",
    "set_csrf_cookie",
]
