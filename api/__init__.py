"""Эндпоинты API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def api_health_check():
    """API проверка работоспособности."""
    return {"status": "ok", "api": True}

