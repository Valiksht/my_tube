"""API роутеры для видео.

Загрузка, просмотр, обновление, удаление видео.
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user, get_optional_user, require_role
from app.schemas.video import VideoCreate, VideoUpdate, VideoResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.video import VideoService
from app.services.comment import CommentService
from app.models.users import User

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", response_model=list[VideoResponse])
async def list_videos(
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(50, ge=1, le=100, description="Максимум записей"),
    db: AsyncSession = Depends(get_db),
):
    """Получить список публичных видео."""
    service = VideoService(db)
    videos = await service.get_public_videos(skip=skip, limit=limit)
    return videos


@router.get("/search", response_model=list[VideoResponse])
async def search_videos(
    q: str = Query(..., min_length=1, max_length=100, description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Поиск видео по названию."""
    service = VideoService(db)
    videos = await service.search_videos(query=q, skip=skip, limit=limit)
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить видео по ID."""
    service = VideoService(db)
    video = await service.get_video(video_id=video_id, current_user=current_user)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Увеличиваем счётчик просмотров
    await service.increment_view_count(video)
    
    return video


@router.post(
    "",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_video(
    data: VideoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новое видео."""
    service = VideoService(db)
    
    # Получаем канал пользователя
    channel = current_user.channel
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no channel. Create a channel first.",
        )
    
    video = await service.create_video(
        channel_id=channel.id,
        title=data.title,
        description=data.description,
        privacy=data.privacy,
    )
    
    return video


@router.post(
    "/upload",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    privacy: str = Form("public"),
    video_file: UploadFile | None = None,
    thumbnail_file: UploadFile | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить новое видео с файлом.
    
    Args:
        title: Название видео.
        description: Описание.
        privacy: Тип приватности (public/unlisted/private).
        video_file: Файл видео.
        thumbnail_file: Файл превью (опционально).
        current_user: Текущий пользователь.
        db: Сессия БД.
    """
    from app.storage.base import BaseStorage
    from app.core.exceptions import ValidationException
    
    service = VideoService(db)
    
    # Получаем канал пользователя
    channel = current_user.channel
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no channel. Create a channel first.",
        )
    
    # Проверяем тип файла видео
    allowed_video_types = [
        "video/mp4",
        "video/webm",
        "video/ogg",
        "video/mp2t",
        "application/octet-stream",
    ]
    
    if video_file:
        if video_file.content_type not in allowed_video_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid video type: {video_file.content_type}. Allowed: {', '.join(allowed_video_types)}",
            )
        
        # Проверяем размер файла (макс 2GB)
        video_file.file.seek(0, 2)  # Переходим в конец
        file_size = video_file.file.tell()
        video_file.file.seek(0)  # Возвращаемся в начало
        
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size: 2GB",
            )
    
    # Создаём запись видео в БД
    video = await service.create_video(
        channel_id=channel.id,
        title=title,
        description=description,
        privacy=privacy,
    )
    
    # Загружаем видео файл
    if video_file:
        video = await service.upload_video_file(
            video,
            video_file.file,
            content_type=video_file.content_type or "video/mp4",
            size=file_size,
        )
    
    # Загружаем превью
    if thumbnail_file and thumbnail_file.filename:
        allowed_thumb_types = ["image/jpeg", "image/png", "image/webp"]
        if thumbnail_file.content_type not in allowed_thumb_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid thumbnail type: {thumbnail_file.content_type}",
            )
        
        video = await service.upload_thumbnail(
            video,
            thumbnail_file.file,
            content_type=thumbnail_file.content_type,
        )
    
    return video


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    data: VideoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить видео."""
    service = VideoService(db)
    
    video = await service.get_video(video_id=video_id, current_user=current_user)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    try:
        video = await service.update_video(video, current_user, data)
        return video
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить видео."""
    service = VideoService(db)
    
    video = await service.get_video(video_id=video_id, current_user=current_user)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    await service.delete_video(video)


# ==================== Комментарии ====================


@router.get("/{video_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    video_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Получить комментарии видео."""
    service = CommentService(db)
    comments = await service.get_video_comments(
        video_id=video_id,
        skip=skip,
        limit=limit,
    )
    return comments


@router.post(
    "/{video_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    video_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать комментарий."""
    service = CommentService(db)
    
    comment = await service.create_comment(
        video_id=video_id,
        user_id=current_user.id,
        content=data.content,
    )
    
    return comment


@router.delete(
    "/{video_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    video_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить комментарий."""
    service = CommentService(db)

    from app.models.comment import Comment
    from sqlalchemy import select

    query = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    await service.delete_comment(comment, current_user)
