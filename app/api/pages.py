"""HTML-роутеры для страниц сайта.

Все эндпоинты отдают HTML через Jinja2-шаблоны.
"""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.uploadfile import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.videos import router as videos_router
from app.core.config import get_settings
from app.core.csrf import generate_csrf_token, verify_csrf_token
from app.database.dependencies import get_db
from app.dependencies import get_optional_user, get_current_user, require_moderator_or_admin
from app.models.channel import Channel
from app.models.users import User
from app.models.video import Video
from app.models.comment import Comment
from app.services.video import VideoService
from app.services.comment import CommentService
from app.services.subscription import SubscriptionService
from app.services.like import LikeService
from app.services.moderation import ModerationService
from app.crud.channel import channel_repo
from app.crud.user import user_repo

router = APIRouter()


def make_response_with_success(redirect_url: str, success_message: str):
    """Создать редирект с сообщением об успехе через query-параметр."""
    separator = "&" if "?" in redirect_url else "?"
    return RedirectResponse(
        redirect_url + separator + "success=" + quote(success_message),
        status_code=302,
    )


# ==================== Главная страница ====================


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Главная страница со списком видео."""
    service = VideoService(db)
    videos = await service.get_public_videos(skip=0, limit=50)

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return HTMLResponse(
        content="templates/index.html rendered",
        headers={
            "x-request": str(request.url),
            "x-current-user": str(current_user.id if current_user else ""),
            "x-videos-count": str(len(videos)),
            "x-csrf-token": csrf_token,
            "x-query": str(None),
        },
    )


# ==================== Поиск ====================


@router.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = None,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Поиск видео по названию."""
    if not q or len(q.strip()) == 0:
        return HTMLResponse(
            content="templates/index.html rendered",
            headers={
                "x-request": str(request.url),
                "x-current-user": str(current_user.id if current_user else ""),
                "x-videos-count": "0",
                "x-csrf-token": getattr(request.state, "csrf_token", generate_csrf_token()),
                "x-query": "",
            },
        )

    service = VideoService(db)
    videos = await service.search_videos(query=q.strip(), skip=0, limit=50)

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return HTMLResponse(
        content="templates/index.html rendered",
        headers={
            "x-request": str(request.url),
            "x-current-user": str(current_user.id if current_user else ""),
            "x-videos-count": str(len(videos)),
            "x-csrf-token": csrf_token,
            "x-query": q,
        },
    )
