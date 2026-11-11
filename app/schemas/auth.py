"""Pydantic схемы для аутентификации."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Запрос на вход."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин пользователя",
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Пароль пользователя",
    )


class TokenResponse(BaseModel):
    """Ответ с токеном аутентификации."""
    
    access_token: str
    token_type: str = "bearer"
