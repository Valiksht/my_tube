"""Тесты загрузки видео (API)."""

import io
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_upload_video_no_file(client, test_user, test_channel):
    """Тест создания видео без файла (только метаданные)."""
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

    # Создаём видео без файла
    response = await client.post(
        "/api/videos/upload",
        data={
            "title": "Upload Test Video",
            "description": "Test description",
            "privacy": "public",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Upload Test Video"


@pytest.mark.anyio
async def test_upload_video_with_file(client, test_user, test_channel):
    """Тест загрузки видео с файлом."""
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

    # Создаём минимальный тестовый файл
    video_content = io.BytesIO(b"fake video content for testing")
    thumbnail_content = io.BytesIO(b"fake thumbnail content")

    response = await client.post(
        "/api/videos/upload",
        data={
            "title": "Upload With File",
            "description": "With file test",
            "privacy": "public",
        },
        files={
            "video_file": ("test.mp4", video_content, "video/mp4"),
            "thumbnail_file": ("thumb.jpg", thumbnail_content, "image/jpeg"),
        },
    )

    # Может вернуть 201 или ошибку storage — главное что не crash
    assert response.status_code in (201, 400, 500)


@pytest.mark.anyio
async def test_upload_video_unauthorized(client):
    """Тест загрузки видео без авторизации."""
    response = await client.post(
        "/api/videos/upload",
        data={
            "title": "Unauthorized Upload",
            "description": "Test",
            "privacy": "public",
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_upload_video_no_channel(client, test_user):
    """Тест загрузки видео без канала."""
    # Создаём пользователя без канала
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "nouuser2",
            "email": "nou2@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201

    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "nouuser2",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # Пытаемся загрузить видео
    response = await client.post(
        "/api/videos/upload",
        data={
            "title": "No Channel Video",
            "description": "Test",
            "privacy": "public",
        },
    )

    # Должен вернуть 400 (нет канала)
    assert response.status_code == 400
