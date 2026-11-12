"""Тесты комментариев."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_list_comments(client, test_video):
    """Тест получения списка комментариев."""
    response = await client.get(f"/api/videos/{test_video.id}/comments")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_create_comment(client, test_user, test_video):
    """Тест создания комментария."""
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

    # Создаём комментарий
    response = await client.post(
        f"/api/videos/{test_video.id}/comments",
        json={"content": "Great video!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Great video!"
    assert "id" in data


@pytest.mark.anyio
async def test_create_comment_unauthorized(client, test_video):
    """Тест создания комментария без авторизации."""
    response = await client.post(
        f"/api/videos/{test_video.id}/comments",
        json={"content": "Spam comment"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_delete_comment(client, test_user, test_video):
    """Тест удаления комментария владельцем."""
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

    # Создаём комментарий
    create_response = await client.post(
        f"/api/videos/{test_video.id}/comments",
        json={"content": "My comment"},
    )
    assert create_response.status_code == 201
    comment_id = create_response.json()["id"]

    # Удаляем комментарий
    response = await client.delete(
        f"/api/videos/{test_video.id}/comments/{comment_id}"
    )

    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_comment_unauthorized(client, test_video):
    """Тест удаления комментария без авторизации."""
    response = await client.delete(
        f"/api/videos/{test_video.id}/comments/999"
    )

    assert response.status_code == 401
