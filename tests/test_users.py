"""Тесты пользователей (API)."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_get_user(client, test_user):
    """Тест получения пользователя по ID."""
    response = await client.get(f"/api/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_get_user_not_found(client):
    """Тест получения несуществующего пользователя."""
    response = await client.get("/api/users/99999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_me(client, test_user):
    """Тест получения текущего пользователя."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.anyio
async def test_get_me_unauthorized(client):
    """Тест получения текущего пользователя без авторизации."""
    response = await client.get("/api/users/me")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_update_me(client, test_user):
    """Тест обновления данных текущего пользователя."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.patch(
        "/api/users/me",
        json={"username": "updateduser"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"


@pytest.mark.anyio
async def test_update_me_unauthorized(client):
    """Тест обновления данных без авторизации."""
    response = await client.patch(
        "/api/users/me",
        json={"username": "hacker"},
    )

    assert response.status_code == 401
