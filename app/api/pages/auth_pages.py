"""HTML-роутеры для аутентификации: login, register, logout."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, Request, status, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse

from app.core.config import get_settings
from app.core.csrf import generate_csrf_token, csrf_protect_form
from app.database.dependencies import get_db
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _make_redirect(url: str, message: str):
    """Создать редирект с сообщением об успехе через query-параметр."""
    separator = "&" if "?" in url else "?"
    return RedirectResponse(
        url + separator + "success=" + quote(message),
        status_code=302,
    )


# ==================== Login ====================


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    error: str = None,
    success: str = None,
):
    """Страница входа."""
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return request.app.templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "success": success,
        "csrf_token": csrf_token,
    })


@router.post("/login")
async def login_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка входа."""
    from app.services.auth import AuthService

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

        response = _make_redirect("/", "Вы успешно вошли в аккаунт")
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


# ==================== Register ====================


@router.get("/register", response_class="HTMLResponse")
async def register_page(
    request: Request,
    error: str = None,
):
    """Страница регистрации."""
    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())
    return request.app.templates.TemplateResponse("register.html", {
        "request": request,
        "error": error,
        "csrf_token": csrf_token,
    })


@router.post("/register")
async def register_submit(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Обработка регистрации."""
    from app.services.auth import AuthService

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

        response = _make_redirect("/", "Регистрация прошла успешно!")
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



