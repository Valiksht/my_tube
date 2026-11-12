"""Тесты лайков."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_toggle_like(client, test_user, test_video):
    """Тест переключения лайка."""
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

    # Ставим лайк
    response = await client.post(
        f"/api/videos/{test_video.id}/likes"
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.anyio
async def test_toggle_like_again(client, test_user, test_video):
    """Тест повторного переключения лайка (снять лайк)."""
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

    # Ставим лайк
    await client.post(f"/api/videos/{test_video.id}/likes")

    # Снимаем лайк
    response = await client.post(
        f"/api/videos/{test_video.id}/likes"
    )

    # Должен вернуть 200 (лайк снят)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_like_status(client, test_user, test_video):
    """Тест проверки статуса лайка."""
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

    # Ставим лайк
    await client.post(f"/api/videos/{test_video.id}/likes")

    # Проверяем статус
    response = await client.get(
        f"/api/videos/{test_video.id}/likes/status"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_liked"] is True


@pytest.mark.anyio
async def test_like_count(client, test_user, test_video):
    """Тест получения количества лайков."""
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

    # Ставим лайк
    await client.post(f"/api/videos/{test_video.id}/likes")

    # Получаем количество
    response = await client.get(
        f"/api/videos/{test_video.id}/likes/count"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["like_count"] >= 1


@pytest.mark.anyio
async def test_like_status_unauthorized(client, test_video):
    """Тест проверки статуса лайка без авторизации."""
    response = await client.get(
        f"/api/videos/{test_video.id}/likes/status"
    )

    assert response.status_code == 401
