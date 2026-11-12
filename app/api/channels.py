"""API роутеры для каналов и пользователей."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user, require_role
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.video import VideoService
from app.models.channel import Channel
from app.models.users import User
from app.crud.channel import channel_repo

router = APIRouter(tags=["channels", "users"])


# ==================== Каналы ====================


@router.get("/channels/me", response_model=ChannelResponse)
async def get_my_channel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить мой канал."""
    channel = current_user.channel
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found. Create a channel first.",
        )
    return channel


@router.post(
    "/channels",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать канал."""
    # Проверяем что у пользователя ещё нет канала
    existing = await channel_repo.get_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a channel",
        )
    
    channel = await channel_repo.create_channel(
        db,
        user_id=current_user.id,
        name=data.name,
        description=data.description,
    )
    
    return channel


@router.patch("/channels/me", response_model=ChannelResponse)
async def update_my_channel(
    data: ChannelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить мой канал."""
    channel = current_user.channel
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    
    channel_dict = data.model_dump(exclude_unset=True)
    channel = await channel_repo.update(db, channel, channel_dict)
    
    return channel


@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить канал по ID."""
    channel = await channel_repo.get_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return channel


@router.get("/channels/{channel_id}/videos", response_model=list[dict])
async def get_channel_videos(
    channel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Получить видео канала."""
    channel = await channel_repo.get_by_id(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    
    service = VideoService(db)
    videos = await service.get_user_videos(
        channel_id=channel_id,
        skip=skip,
        limit=limit,
    )
    
    return [
        {
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "duration": v.duration,
            "view_count": v.view_count,
            "privacy": v.privacy,
            "created_at": v.created_at.isoformat(),
        }
        for v in videos
    ]


# ==================== Пользователи ====================


@router.get("/users/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Получить данные текущего пользователя."""
    return current_user


@router.patch("/users/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить данные текущего пользователя."""
    from app.crud.user import user_repo

    update_data = data.model_dump(exclude_unset=True)

    if "password" in data.model_fields_set:
        from app.core.security import hash_password
        update_data["hashed_password"] = hash_password(data.password)  # type: ignore[union-attr]

    user = await user_repo.update(db, current_user, update_data)

    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить пользователя по ID."""
    from app.crud.user import user_repo

    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
