"""Главный файл приложения YouTube Clone."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import get_settings
from app.api.__init__ import router as api_router
from app.database.dependencies import get_db
from app.dependencies import get_optional_user
from app.services.video import VideoService
from app.services.comment import CommentService
from app.services.subscription import SubscriptionService
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession

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


@app.get("/health")
def health_check():
    """Проверка работоспособности приложения."""
    return {"status": "ok", "app": settings.app_name}


# ==================== HTML Роутеры ====================


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Главная страница со списком видео."""
    service = VideoService(db)
    videos = await service.get_public_videos(skip=0, limit=50)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "videos": videos,
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    error: str = None,
):
    """Страница входа."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
    })


@app.post("/login")
async def login_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка входа."""
    from app.services.auth import AuthService
    from app.core.config import get_settings
    
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
        return RedirectResponse("/login?error=Введите логин и пароль", status_code=303)
    
    try:
        service = AuthService(db)
        session = await service.login(
            username=username,
            password=password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        response = RedirectResponse("/", status_code=302)
        settings = get_settings()
        
        response.set_cookie(
            cookie_name=settings.session_cookie,
            value=session.session_id,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=settings.session_max_age,
        )
        
        return response
        
    except ValueError as e:
        return RedirectResponse(f"/login?error={str(e)}", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    error: str = None,
):
    """Страница регистрации."""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error,
    })


@app.post("/register")
async def register_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка регистрации."""
    from app.services.auth import AuthService
    
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")
    
    if not all([username, email, password]):
        return RedirectResponse("/register?error=Заполните все поля", status_code=303)
    
    if password != password_confirm:
        return RedirectResponse("/register?error=Пароли не совпадают", status_code=303)
    
    if len(password) < 8:
        return RedirectResponse("/register?error=Пароль минимум 8 символов", status_code=303)
    
    try:
        service = AuthService(db)
        await service.register(
            username=username,
            email=email,
            password=password,
        )
        
        # Автоматический вход после регистрации
        session = await service.login(username=username, password=password)
        
        response = RedirectResponse("/", status_code=302)
        settings = get_settings()
        
        response.set_cookie(
            cookie_name=settings.session_cookie,
            value=session.session_id,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=settings.session_max_age,
        )
        
        return response
        
    except ValueError as e:
        return RedirectResponse(f"/register?error={str(e)}", status_code=303)


@app.post("/api/auth/logout")
async def logout_submit(
    request: Request,
):
    """Выход из аккаунта."""
    from app.services.auth import AuthService
    from app.core.config import get_settings
    
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie)
    
    if not session_id:
        return RedirectResponse("/", status_code=302)
    
    try:
        async for db in get_db():
            service = AuthService(db)
            await service.logout(session_id)
            break
    except:
        pass
    
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie(key=settings.session_cookie, path="/")
    
    return response


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: User = Depends(get_optional_user),
    error: str = None,
):
    """Страница загрузки видео."""
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "current_user": current_user,
        "error": error,
    })


@app.post("/upload")
async def upload_submit(
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Обработка загрузки видео."""
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    from app.services.video import VideoService
    from app.storage.minio import MinIOStorage
    
    title = request.form.get("title")
    description = request.form.get("description", "")
    privacy = request.form.get("privacy", "public")
    video_file = request.form.get("video_file")
    thumbnail_file = request.form.get("thumbnail_file")
    
    if not title:
        return RedirectResponse("/upload?error=Введите название видео", status_code=303)
    
    try:
        service = VideoService(db)
        channel = current_user.channel
        
        if not channel:
            return RedirectResponse(
                "/upload?error=Сначала создайте канал",
                status_code=303,
            )
        
        video = await service.create_video(
            channel_id=channel.id,
            title=title,
            description=description,
            privacy=privacy,
        )
        
        return RedirectResponse(f"/video/{video.id}", status_code=302)
        
    except Exception as e:
        return RedirectResponse(f"/upload?error={str(e)}", status_code=303)


@app.get("/video/{video_id}", response_class=HTMLResponse)
async def video_page(
    video_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница просмотра видео."""
    from app.services.video import VideoService
    from app.services.comment import CommentService
    from app.services.subscription import SubscriptionService
    
    service = VideoService(db)
    video = await service.get_video(video_id=video_id, current_user=current_user)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Комментарии
    comment_service = CommentService(db)
    comments = await comment_service.get_video_comments(
        video_id=video_id,
        skip=0,
        limit=50,
    )
    
    # Рекомендации
    recommended = await service.get_public_videos(skip=0, limit=10)
    recommended = [v for v in recommended if v.id != video_id][:5]
    
    # Подписчики
    sub_service = SubscriptionService(db)
    subscriber_count = await sub_service.get_channel_subscriber_count(
        video.channel.id
    )
    
    # Лайки
    like_count = 0  # Можно получить через like_service
    
    return templates.TemplateResponse("video.html", {
        "request": request,
        "video": video,
        "current_user": current_user,
        "comments": comments,
        "recommended_videos": recommended,
        "subscriber_count": subscriber_count,
        "like_count": like_count,
    })


@app.get("/channel/{channel_id}", response_class=HTMLResponse)
async def channel_page(
    channel_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница канала."""
    from app.crud.channel import channel_repo
    from app.services.video import VideoService
    from app.services.subscription import SubscriptionService
    
    channel = await channel_repo.get_by_id(db, channel_id)
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    user = channel.user
    
    # Видео канала
    video_service = VideoService(db)
    videos = await video_service.get_user_videos(
        channel_id=channel_id,
        skip=0,
        limit=50,
    )
    
    # Подписчики
    sub_service = SubscriptionService(db)
    subscriber_count = await sub_service.get_channel_subscriber_count(
        channel_id=channel_id
    )
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "current_user": current_user,
        "videos": videos,
        "subscriber_count": subscriber_count,
    })


@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def profile_page(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница профиля пользователя."""
    from app.crud.user import user_repo
    from app.services.video import VideoService
    from app.services.subscription import SubscriptionService
    
    user = await user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Видео пользователя
    video_service = VideoService(db)
    videos = []
    
    if user.channel:
        videos = await video_service.get_user_videos(
            channel_id=user.channel.id,
            skip=0,
            limit=50,
        )
    
    # Подписчики
    subscriber_count = 0
    if user.channel:
        sub_service = SubscriptionService(db)
        subscriber_count = await sub_service.get_channel_subscriber_count(
            channel_id=user.channel.id
        )
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "current_user": current_user,
        "videos": videos,
        "subscriber_count": subscriber_count,
    })


# Подключение API роутов
app.include_router(api_router, prefix="/api")
