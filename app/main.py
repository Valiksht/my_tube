"""Главный файл приложения YouTube Clone."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.core.csrf import generate_csrf_token
from app.api.__init__ import router as api_router
from app.api.pages import pages_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    yield


app = FastAPI(
    title=settings.app_name,
    description="Клон YouTube с функционалом загрузки видео, комментариев, лайков и т.д.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except FileNotFoundError:
    pass

# HTML шаблоны
templates = Jinja2Templates(directory="app/templates")
app.templates = templates


# ==================== CSRF Middleware ====================

@app.middleware("http")
async def add_csrf_token(request: Request, call_next):
    """Добавить CSRF-токен в контекст шаблонов и установить Cookie для GET-запросов.
    
    Токен генерируется ОДИН РАЗ при первом GET и используется для всех страниц.
    Это предотвращает рассинхронизацию между токеном в форме и cookie.
    """
    csrf_cookie_name = settings.session_cookie + "_csrf"

    # GET-запрос: используем существующий cookie или генерируем новый
    if request.method == "GET":
        existing_token = request.cookies.get(csrf_cookie_name)
        if existing_token:
            csrf_token = existing_token
        else:
            csrf_token = generate_csrf_token()

        request.state.csrf_token = csrf_token

        response = await call_next(request)

        # Установить cookie только если его ещё нет
        if not existing_token:
            response.set_cookie(
                key=csrf_cookie_name,
                value=csrf_token,
                httponly=True,
                samesite="lax",
                path="/",
            )

        return response

    # POST и другие методы: cookie уже установлен предыдущим GET-запросом
    return await call_next(request)


@app.get("/health")
def health_check():
    """Проверка работоспособности приложения."""
    return {"status": "ok", "app": settings.app_name}


# Подключение API роутов
app.include_router(api_router, prefix="/api")

# Подключение HTML-роутов (без префикса /api)
app.include_router(pages_router)
