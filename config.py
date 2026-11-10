import os
from functools import lru_cache

class Settings:
    def __init__(self):
        # Базовые настройки
        self.APP_NAME = "YouTube Clone"
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        # Настройки базы данных (PostgreSQL)
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost:5432/mytube_db"
        )
        
        # Секреты (замените на свои!)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.ALGORITHM = "HS256"
        
        # CORS
        self.CORS_ORIGINS = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://127.0.0.1:8000"
        ).split(",")

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
