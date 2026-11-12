"""API роутеры для аутентификации.

Регистрация, вход, выход, текущий пользователь.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user, get_optional_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService
from app.core.exceptions import (
    AuthenticationRequiredException,
)
from app.core.config import get_settings
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Зарегистрировать нового пользователя.
    
    Args:
        data: Данные пользователя.
        request: FastAPI Request.
        db: Сессия базы данных.
        
    Returns:
        Созданный пользователь.
    """
    settings = get_settings()
    
    try:
        service = AuthService(db)
        user = await service.register(
            username=data.username,
            email=data.email,
            password=data.password,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Войти в аккаунт.
    
    Args:
        data: Логин и пароль.
        request: FastAPI Request (содержит Cookie и headers).
        db: Сессия базы данных.
        
    Returns:
        Токен доступа.
    """
    from app.core.csrf import set_csrf_cookie
    
    settings = get_settings()
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        service = AuthService(db)
        session = await service.login(
            username=data.username,
            password=data.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        response = JSONResponse(
            content={
                "access_token": session.session_id,
                "token_type": "session",
            }
        )
        
        # Устанавливаем session Cookie
        response.set_cookie(
            key=settings.session_cookie,
            value=session.session_id,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=settings.session_max_age,
        )
        
        # Устанавливаем CSRF Cookie
        set_csrf_cookie(response)
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Выйти из аккаунта.
    
    Отзывает текущую сессию и очищает Cookie.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    
    session_id = request.cookies.get(settings.session_cookie)
    if not session_id:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    service = AuthService(db)
    await service.logout(session_id)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=settings.session_cookie,
        path="/",
    )
    response.delete_cookie(
        key=settings.session_cookie + "_csrf",
        path="/",
    )
    
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Получить данные текущего пользователя.
    
    Requires authentication.
    
    Returns:
        Данные пользователя.
    """
    return current_user


@router.get("/check")
async def check_auth(
    current_user: User = Depends(get_optional_user),
):
    """Проверить авторизацию.
    
    Returns:
        {"authenticated": true, "user": {...}} или {"authenticated": false}
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role,
            },
        }
    return {"authenticated": False}
