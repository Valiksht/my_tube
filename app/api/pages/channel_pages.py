"""HTML-роутеры для каналов, профилей и создания/редактирования каналов."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.csrf import generate_csrf_token, csrf_protect_form
from app.crud.channel import channel_repo
from app.crud.user import user_repo
from app.database.dependencies import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.channel import Channel
from app.models.users import User
from app.services.video import VideoService
from app.services.subscription import SubscriptionService

router = APIRouter()


# ==================== Страница канала ====================

# Статические маршруты ДО динамических,
# иначе FastAPI попытается сопоставить "/channel/create"
# с маршрутом "/channel/{channel_id}" и вернёт 422.


@router.get("/channel/create", response_class=HTMLResponse)
async def create_channel_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    error: str = None,
    success: str = None,
):
    """Страница создания канала."""
    existing = await channel_repo.get_by_user_id(db, current_user.id)

    if existing:
        return RedirectResponse(
            f"/channel/{existing.id}", status_code=302
        )

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse("create_channel.html", {
        "request": request,
        "current_user": current_user,
        "error": error,
        "success": success,
        "csrf_token": csrf_token,
    })


@router.post("/channel/create")
async def create_channel_submit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание канала."""
    form = await request.form()
    await csrf_protect_form(request, form=dict(form))

    name = form.get("name", "")
    description = form.get("description", "")

    if not name or len(name.strip()) < 2:
        return RedirectResponse(
            "/channel/create?error=Название канала должно содержать минимум 2 символа",
            status_code=303,
        )

    existing = await channel_repo.get_by_user_id(db, current_user.id)
    if existing:
        return RedirectResponse(
            f"/channel/{existing.id}", status_code=302
        )

    try:
        channel = await channel_repo.create_channel(
            db,
            user_id=current_user.id,
            name=name.strip(),
            description=description.strip(),
        )

        return RedirectResponse(
            f"/channel/{channel.id}?success=Канал успешно создан!",
            status_code=302,
        )

    except Exception as e:
        return RedirectResponse(f"/channel/create?error={str(e)}", status_code=303)


@router.get("/channel/edit/{channel_id}", response_class=HTMLResponse)
async def edit_channel_page(
    channel_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    error: str = None,
):
    """Страница редактирования канала."""
    channel = await channel_repo.get_by_id_with(
        db, channel_id, selectinload(Channel.user),
    )

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel.user.id != current_user.id:
        return RedirectResponse("/upload?error=Доступ запрещён", status_code=303)

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse("edit_channel.html", {
        "request": request,
        "current_user": current_user,
        "channel": channel,
        "error": error,
        "csrf_token": csrf_token,
    })


@router.post("/channel/edit/{channel_id}")
async def edit_channel_submit(
    channel_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование канала."""
    form = await request.form()
    await csrf_protect_form(request, form=dict(form))

    name = form.get("name", "")
    description = form.get("description", "")

    channel = await channel_repo.get_by_id_with(
        db, channel_id, selectinload(Channel.user),
    )

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel.user.id != current_user.id:
        return RedirectResponse("/upload?error=Доступ запрещён", status_code=303)

    if not name or len(name.strip()) < 2:
        return RedirectResponse(
            f"/channel/edit/{channel_id}?error=Название канала должно содержать минимум 2 символа",
            status_code=303,
        )

    try:
        await channel_repo.update(db, channel, {
            "name": name.strip(),
            "description": description.strip(),
        })

        return RedirectResponse(
            f"/channel/{channel_id}?success=Канал успешно обновлён!",
            status_code=302,
        )

    except Exception as e:
        return RedirectResponse(f"/channel/edit/{channel_id}?error={str(e)}", status_code=303)


# Динамический маршрут — ПОСЛЕ всех статических


@router.get("/channel/{channel_id}", response_class=HTMLResponse)
async def channel_page(
    channel_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    success: str = None,
):
    """Страница канала."""
    channel = await channel_repo.get_by_id_with(
        db, channel_id, selectinload(Channel.user),
    )

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    user = channel.user

    video_service = VideoService(db)
    videos = await video_service.get_user_videos(
        channel_id=channel_id, skip=0, limit=50,
    )

    sub_service = SubscriptionService(db)
    subscriber_count = await sub_service.get_channel_subscriber_count(channel_id=channel_id)

    is_subscribed = False
    if current_user:
        is_subscribed = await sub_service.is_subscribed(
            subscribed_user_id=current_user.id,
            subscribed_channel_id=channel_id,
        )

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "current_user": current_user,
        "channel": channel,
        "videos": videos,
        "subscriber_count": subscriber_count,
        "csrf_token": csrf_token,
        "is_subscribed": is_subscribed,
        "success": success,
    })


# ==================== Страница профиля ====================


@router.get("/profile/{user_id}", response_class=HTMLResponse)
async def profile_page(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница профиля пользователя."""
    user = await user_repo.get_by_id_with(
        db, user_id, selectinload(User.channel),
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    videos = []
    subscriber_count = 0
    is_subscribed = False
    channel = None

    if user.channel:
        channel = user.channel
        video_service = VideoService(db)
        videos = await video_service.get_user_videos(
            channel_id=channel.id, skip=0, limit=50,
        )

        sub_service = SubscriptionService(db)
        subscriber_count = await sub_service.get_channel_subscriber_count(
            channel_id=channel.id,
        )
        if current_user:
            is_subscribed = await sub_service.is_subscribed(
                subscribed_user_id=current_user.id,
                subscribed_channel_id=channel.id,
            )

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "current_user": current_user,
        "channel": channel,
        "videos": videos,
        "subscriber_count": subscriber_count,
        "csrf_token": csrf_token,
        "is_subscribed": is_subscribed,
    })
