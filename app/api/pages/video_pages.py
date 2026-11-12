"""HTML-роутеры для видео: главная, загрузка, просмотр, поиск."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.csrf import generate_csrf_token
from app.database.dependencies import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.channel import Channel
from app.models.users import User
from app.services.video import VideoService
from app.services.comment import CommentService
from app.services.subscription import SubscriptionService
from app.services.like import LikeService

router = APIRouter()


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

    return request.app.templates.TemplateResponse(request, "index.html", {
        "current_user": current_user,
        "videos": videos,
        "csrf_token": csrf_token,
        "query": None,
    })


# ==================== Загрузка видео ====================


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    error: str = None,
    success: str = None,
):
    """Страница загрузки видео."""
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return request.app.templates.TemplateResponse(request, "upload.html", {
        "current_user": current_user,
        "error": error,
        "success": success,
        "csrf_token": csrf_token,
    })


@router.post("/upload")
async def upload_submit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обработка загрузки видео."""
    from app.core.config import get_settings

    form = await request.form()

    title = form.get("title", "")
    description = form.get("description", "")
    privacy = form.get("privacy", "public")
    channel_id_str = form.get("channel_id", "")
    video_file = form.get("video_file")
    thumbnail_file = form.get("thumbnail_file")

    if not title:
        return RedirectResponse("/upload?error=Введите название видео", status_code=303)

    if not channel_id_str:
        return RedirectResponse(
            "/upload?error=Выберите канал для загрузки",
            status_code=303,
        )

    try:
        channel_id = int(channel_id_str)
    except (ValueError, TypeError):
        return RedirectResponse(
            "/upload?error=Некорректный ID канала",
            status_code=303,
        )

    try:
        service = VideoService(db)
        channel = current_user.channel

        if not channel:
            return RedirectResponse(
                "/upload?error=У вас нет канала",
                status_code=303,
            )

        if channel.id != channel_id:
            return RedirectResponse(
                "/upload?error=Доступ запрещён",
                status_code=303,
            )

        video = await service.create_video(
            channel_id=channel.id,
            title=title,
            description=description,
            privacy=privacy,
        )

        if video_file:
            content_type = video_file.content_type or "video/mp4"
            video_file.file.seek(0, 2)
            file_size = video_file.file.tell()
            video_file.file.seek(0)

            max_size = 2 * 1024 * 1024 * 1024
            if file_size > max_size:
                return RedirectResponse(
                    "/upload?error=Файл слишком большой. Максимум 2GB",
                    status_code=303,
                )

            await service.upload_video_file(
                video, video_file.file,
                content_type=content_type,
                size=file_size,
            )

        if thumbnail_file and thumbnail_file.filename:
            allowed_thumb_types = ["image/jpeg", "image/png", "image/webp"]
            if thumbnail_file.content_type not in allowed_thumb_types:
                return RedirectResponse(
                    "/upload?error=Неподдерживаемый формат превью. Используйте JPG, PNG или WebP",
                    status_code=303,
                )

            await service.upload_thumbnail(
                video,
                thumbnail_file.file,
                content_type=thumbnail_file.content_type,
            )

        return RedirectResponse(
            f"/video/{video.id}?success=Видео успешно загружено!",
            status_code=302,
        )

    except Exception as e:
        return RedirectResponse(f"/upload?error={str(e)}", status_code=303)


# ==================== Просмотр видео ====================


@router.get("/video/{video_id}", response_class=HTMLResponse)
async def video_page(
    video_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    success: str = None,
):
    """Страница просмотра видео."""
    service = VideoService(db)
    video = await service.get_video(video_id=video_id, current_user=current_user)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    await service.increment_view_count(video)

    comment_service = CommentService(db)
    comments = await comment_service.get_video_comments(
        video_id=video_id, skip=0, limit=50,
    )

    recommended = await service.get_public_videos(skip=0, limit=10)
    recommended = [v for v in recommended if v.id != video_id][:5]

    sub_service = SubscriptionService(db)
    subscriber_count = await sub_service.get_channel_subscriber_count(video.channel.id)

    like_service = LikeService(db)
    like_count = await like_service.get_video_like_count(video_id=video_id)

    is_subscribed = False
    is_liked = False
    if current_user:
        is_subscribed = await sub_service.is_subscribed(
            subscribed_user_id=current_user.id,
            subscribed_channel_id=video.channel.id,
        )
        is_liked = await like_service.get_like_status(
            video_id=video_id,
            user_id=current_user.id,
        )

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse(request, "video.html", {
        "video": video,
        "current_user": current_user,
        "comments": comments,
        "recommended_videos": recommended,
        "subscriber_count": subscriber_count,
        "like_count": like_count,
        "csrf_token": csrf_token,
        "is_subscribed": is_subscribed,
        "is_liked": is_liked,
        "success": success,
    })


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
        return request.app.templates.TemplateResponse(request, "index.html", {
            "current_user": current_user,
            "videos": [],
            "csrf_token": getattr(request.state, "csrf_token", generate_csrf_token()),
            "query": "",
        })

    service = VideoService(db)
    videos = await service.search_videos(query=q.strip(), skip=0, limit=50)

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse(request, "index.html", {
        "current_user": current_user,
        "videos": videos,
        "csrf_token": csrf_token,
        "query": q,
    })
