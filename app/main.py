"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("mytube_app")

app = FastAPI(
    title="YouTube Clone API",
    description="Educational YouTube Clone project with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware для логирования всех запросов."""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.get("/health", tags=["Health"])
async def health_check():
    """Эндпоинт проверки здоровья приложения.

    Проверяет:
    - Подключение к базе данных работает.
    - Сессия SQLAlchemy может быть создана.
    """
    try:
        from app.database.session import get_async_session
        
        async with get_async_session() as session:
            # Проверка, что сессия работает — выполним простой SELECT
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1
            
        return {"status": "healthy", "version": settings.VERSION, "db": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503
