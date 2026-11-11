"""Главный файл приложения YouTube Clone."""

from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import get_settings
from app.core.csrf import generate_csrf_token, verify_csrf_token
from app.api.__init__ import router as api_router
from app.database.dependencies import get_db
from app.dependencies import get_optional_user, get_current_user, require_moderator_or_admin
from app.services.video import VideoService
from app.services.comment import CommentService
from app.services.subscription import SubscriptionService
from app.services.like import LikeService
from app.services.moderation import ModerationService
from app.models.users import User
from app.models.video import Video
from app.models.channel import Channel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

settings = get_settings()


def make_response_with_success(redirect_url: str, success_message: str):
    """Создать редирект с сообщением об успехе через query-параметр."""
    separator = "&" if "?" in redirect_url else "?"
    return RedirectResponse(
        redirect_url + separator + "success=" + quote(success_message),
        status_code=302,
    )


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


# ==================== CSRF Middleware ====================

@app.middleware("http")
async def add_csrf_token(request: Request, call_next):
    """Добавить CSRF-токен в контекст шаблонов и установить Cookie для GET-запросов.
    
    Токен генерируется ОДИН РАЗ при первом GET и используется для всех страниц.
    Это предотвращает рассинхронизацию между токеном в форме и cookie.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
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
    
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "videos": videos,
        "csrf_token": csrf_token,
        "query": None,
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    error: str = None,
    success: str = None,
):
    """Страница входа."""
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "success": success,
        "csrf_token": csrf_token,
    })


@app.post("/login")
async def login_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка входа."""
    from app.services.auth import AuthService
    from app.core.config import get_settings
    from app.core.csrf import set_csrf_cookie, csrf_protect_form
    
    form = await request.form()
    
    await csrf_protect_form(request, form=dict(form))
    
    username = form.get("username")
    password = form.get("password")
    
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
        
        response = make_response_with_success("/", "Вы успешно вошли в аккаунт")
        settings = get_settings()
        
        response.set_cookie(
            key=settings.session_cookie,
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
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error,
        "csrf_token": csrf_token,
    })


@app.post("/register")
async def register_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка регистрации."""
    from app.services.auth import AuthService
    from app.core.config import get_settings
    from app.core.csrf import csrf_protect_form
    
    form = await request.form()
    
    await csrf_protect_form(request, form=dict(form))
    
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    password_confirm = form.get("password_confirm")
    
    if not all([username, email, password]):
        return RedirectResponse("/register?error=Заполните все поля", status_code=303)
    
    if password != password_confirm:
        return RedirectResponse("/register?error=Пароли не совпадают", status_code=303)
    
    if len(password) < 8:
        return RedirectResponse("/register?error=Пароль минимум 8 символов", status_code=303)
    
    try:
        service = AuthService(db)
        user = await service.register(
            username=username,
            email=email,
            password=password,
        )
        
        # Автоматический вход после регистрации
        session = await service.login(username=username, password=password)
        
        response = make_response_with_success("/", "Регистрация прошла успешно!")
        settings = get_settings()
        
        response.set_cookie(
            key=settings.session_cookie,
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
    current_user: User = Depends(get_current_user),
    error: str = None,
    success: str = None,
):
    """Страница загрузки видео."""
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "current_user": current_user,
        "error": error,
        "success": success,
        "csrf_token": csrf_token,
    })


@app.post("/upload")
async def upload_submit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обработка загрузки видео."""
    from app.services.video import VideoService
    from fastapi import UploadFile
    
    form = await request.form()
    
    title = form.get("title", "")
    description = form.get("description", "")
    privacy = form.get("privacy", "public")
    video_file: UploadFile = form.get("video_file")
    thumbnail_file: UploadFile = form.get("thumbnail_file")
    
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
        
        # Создаём запись видео в БД
        video = await service.create_video(
            channel_id=channel.id,
            title=title,
            description=description,
            privacy=privacy,
        )
        
        # Загружаем видео файл в хранилище
        if video_file:
            content_type = video_file.content_type or "video/mp4"
            
            # Проверка размера файла (макс 2GB)
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
                video,
                video_file.file,
                content_type=content_type,
            )
        
        # Загружаем превью (опционально)
        if thumbnail_file:
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
        
        return make_response_with_success(
            f"/video/{video.id}",
            "Видео успешно загружено!",
        )
        
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
    service = VideoService(db)
    video = await service.get_video(video_id=video_id, current_user=current_user)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Увеличить счётчик просмотров
    await service.increment_view_count(video)
    
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
    like_service = LikeService(db)
    like_count = await like_service.get_video_like_count(video_id=video_id)
    
    # Проверка подписки
    is_subscribed = False
    if current_user:
        is_subscribed = await sub_service.is_subscribed(
            subscribed_user_id=current_user.id,
            subscribed_channel_id=video.channel.id,
        )
    
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    
    return templates.TemplateResponse("video.html", {
        "request": request,
        "video": video,
        "current_user": current_user,
        "comments": comments,
        "recommended_videos": recommended,
        "subscriber_count": subscriber_count,
        "like_count": like_count,
        "csrf_token": csrf_token,
        "is_subscribed": is_subscribed,
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
    
    channel = await channel_repo.get_by_id_with(
        db, channel_id, selectinload(Channel.user),
    )
    
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
    
    user = await user_repo.get_by_id_with(
        db, user_id, selectinload(User.channel),
    )
    
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
    is_subscribed = False
    if user.channel:
        sub_service = SubscriptionService(db)
        subscriber_count = await sub_service.get_channel_subscriber_count(
            channel_id=user.channel.id
        )
        if current_user:
            is_subscribed = await sub_service.is_subscribed(
                subscribed_user_id=current_user.id,
                subscribed_channel_id=user.channel.id,
            )
    
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "current_user": current_user,
        "videos": videos,
        "subscriber_count": subscriber_count,
        "csrf_token": csrf_token,
        "is_subscribed": is_subscribed,
    })


@app.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = None,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Поиск видео по названию."""
    if not q or len(q.strip()) == 0:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "current_user": current_user,
            "videos": [],
            "csrf_token": getattr(request.state, "csrf_token", generate_csrf_token()),
            "query": "",
        })
    
    service = VideoService(db)
    videos = await service.search_videos(query=q.strip(), skip=0, limit=50)
    
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "videos": videos,
        "csrf_token": csrf_token,
        "query": q,
    })


@app.get("/moderation", response_class=HTMLResponse)
async def moderation_page(
    request: Request,
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Страница модерации."""
    service = ModerationService(db)
    reports = await service.get_pending_reports(skip=0, limit=100)
    
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    
    # Получаем информацию о репортерах и видео для каждой жалобы
    report_details = []
    for report in reports:
        reporter = None
        video = None
        comment = None
        
        if report.target_type == "video":
            from app.models.video import Video
            result = await db.execute(select(Video).where(Video.id == report.target_id))
            video = result.scalar_one_or_none()
        elif report.target_type == "comment":
            from app.models.comment import Comment
            result = await db.execute(select(Comment).where(Comment.id == report.target_id))
            comment = result.scalar_one_or_none()
        
        # Получаем информацию о репортере
        result = await db.execute(select(User).where(User.id == report.reporter_id))
        reporter = result.scalar_one_or_none()
        
        report_details.append({
            "report": report,
            "reporter": reporter,
            "video": video,
            "comment": comment,
        })
    
    return templates.TemplateResponse("moderation.html", {
        "request": request,
        "current_user": current_user,
        "reports": report_details,
        "csrf_token": csrf_token,
    })


# Подключение API роутов
app.include_router(api_router, prefix="/api")
