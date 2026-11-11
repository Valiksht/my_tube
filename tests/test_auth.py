"""Тесты аутентификации."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.anyio
async def test_register(client: AsyncClient):
    """Тест регистрации пользователя."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.anyio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Тест регистрации с дублирующимся логином."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": test_user.username,
            "email": "other@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Тест регистрации с дублирующимся email."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "otheruser",
            "email": test_user.email,
            "password": "password123",
        },
    )
    
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_weak_password(client: AsyncClient):
    """Тест регистрации со слабым паролем."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "short",
        },
    )
    
    assert response.status_code == 422


@pytest.mark.anyio
async def test_login_success(client: AsyncClient, db_session):
    """Тест успешного входа."""
    from app.core.security import hash_password
    from app.models.users import User
    from datetime import datetime, timezone
    
    user = User(
        username="logintest",
        email="login@example.com",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    
    db_session.add(user)
    await db_session.flush()
    
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "logintest",
            "password": "testpass123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "session"


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Тест входа с неверным паролем."""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_nonexistent_user(client: AsyncClient):
    """Тест входа с несуществующим пользователем."""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Тест получения текущего пользователя без авторизации."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    """Тест проверки работоспособности."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
