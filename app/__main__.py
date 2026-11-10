'__main__.py'

from uvicorn import run
from app.core.config import settings

if __name__ == "__main__":
    # Используем конфигурацию из .env, если она есть
    host = settings.HOST or "127.0.0.1"
    port = settings.PORT or 8000
    reload = settings.RELOAD

    print(f'Запуск приложения: http://{host}:{port}')
    run(
        'app.main:app',
        host=host,
        port=port,
        reload=reload,
        log_level='info'
    )
