from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title="My Tube API",
        description="REST API для video платформы",
        version="1.0.0",
    )

    @app.get("/")
    async def root():
        return {"message": "Welcome to My Tube API!"}

    return app


# Создание экземпляра приложения
app = create_app()


# Запуск через uvicorn:
#   uvicorn main:app --reload --port 8000