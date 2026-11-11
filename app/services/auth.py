"""Сервисы аутентификации и авторизации.

Управляет регистрацией, входом, выходом и проверкой сессий.
Использует серверные сессии с HttpOnly Cookie.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, hash_password
from app.core.csrf import generate_csrf_token
from app.models.users import User
from app.models.session import UserSession
from app.schemas.user import UserCreate
from app.crud.user import user_repo


class AuthService:
    """Сервис аутентификации."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """Зарегистрировать нового пользователя.
        
        Args:
            username: Логин.
            email: Email.
            password: Пароль.
            
        Returns:
            Созданный пользователь.
            
        Raises:
            Exception: Если пользователь уже существует.
        """
        existing = await user_repo.get_by_username(self.db, username)
        if existing:
            raise ValueError(f"User '{username}' already exists")
        
        existing_email = await user_repo.get_by_email(self.db, email)
        if existing_email:
            raise ValueError(f"Email '{email}' already in use")
        
        user = await user_repo.create_user(
            self.db,
            username=username,
            email=email,
            password=password,
        )
        
        return user
    
    async def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Войти в аккаунт и создать сессию.
        
        Args:
            username: Логин.
            password: Пароль.
            ip_address: IP адрес клиента.
            user_agent: User-Agent браузера.
            
        Returns:
            Созданная сессия.
            
        Raises:
            Exception: Если неверные учётные данные.
        """
        user = await user_repo.get_by_username(self.db, username)
        if not user:
            raise ValueError("Invalid username or password")
        
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        # Генерируем сессию
        session_id = generate_csrf_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=7
        )
        
        session = UserSession(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at,
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        
        return session
    
    async def get_current_user(
        self,
        session_id: str,
    ) -> Optional[User]:
        """Получить текущего пользователя по session_id.
        
        Args:
            session_id: Идентификатор сессии из Cookie.
            
        Returns:
            Пользователь или None.
        """
        query = (
            select(UserSession)
            .options(selectinload(UserSession.user))
            .where(
                UserSession.session_id == session_id,
                UserSession.is_active.is_(True),
                UserSession.expires_at > datetime.now(timezone.utc),
            )
            .join(User)
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        return session.user
    
    async def logout(self, session_id: str) -> None:
        """Выйти из аккаунта — отозвать сессию.
        
        Args:
            session_id: Идентификатор сессии.
        """
        query = (
            select(UserSession)
            .where(UserSession.session_id == session_id)
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            await self.db.flush()
    
    async def revoke_all_sessions(self, user_id: int) -> None:
        """Отозвать все сессии пользователя.
        
        Args:
            user_id: ID пользователя.
        """
        query = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active.is_(True),
            )
        )
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
        
        await self.db.flush()

