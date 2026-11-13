"""API роутеры для лайков."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user
from app.services.like import LikeService
from app.models.users import User

router = APIRouter(prefix="/videos/{video_id}/likes", tags=["likes"])


@router.post("")
async def toggle_like(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Установить или удалить лайк."""

    service = LikeService(db)

    is_liked = await service.toggle_like(
        video_id=video_id,
        user_id=current_user.id,
    )

    count = await service.get_video_like_count(
        video_id=video_id,
    )

    return {
        "video_id": video_id,
        "is_liked": is_liked,
        "like_count": count,
    }


@router.get("/status")
async def get_like_status(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Проверить есть ли лайк у пользователя."""
    service = LikeService(db)
    
    is_liked = await service.get_like_status(
        video_id=video_id,
        user_id=current_user.id,
    )
    
    return {"is_liked": is_liked}


@router.get("/count")
async def get_like_count(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить количество лайков на видео."""
    service = LikeService(db)
    
    count = await service.get_video_like_count(video_id=video_id)
    
    return {"like_count": count}
