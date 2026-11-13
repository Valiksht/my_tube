"""Pydantic схемы для пользователей."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин пользователя",
    )
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
    )


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль (минимум 8 символов)",
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""
    
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="Логин пользователя",
    )
    email: EmailStr | None = Field(
        None,
        description="Email пользователя",
    )


class UserResponse(UserBase):
    """Ответ с данными пользователя."""
    
    id: int
    is_active: bool
    role: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
