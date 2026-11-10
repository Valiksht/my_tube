"""Главный файл приложения."""

from fastapi import FastAPI
from api.__init__ import router as api_router

app = FastAPI(
    title="YouTube Clone API",
    description="Клон YouTube с функционалом загрузки видео, комментариев, лайков и т.д.",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    """Проверка работоспособности приложения."""
    return {"status": "ok"}


# Подключение API роутов
app.include_router(api_router, prefix="/api")
