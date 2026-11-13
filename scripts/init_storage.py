"""Скрипт инициализации объектного хранилища.

Проверяет доступность хранилища Garage/MinIO.
Бакет создаётся автоматически при первой загрузке файла.
"""

import asyncio
import os
import sys


def wait_for_storage(host: str, port: int, secure: bool, timeout: int = 60) -> bool:
    """Ожидание готовности хранилища."""
    import socket
    
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        asyncio.sleep(2)
    
    return False


async def ensure_storage_available() -> bool:
    """Проверить доступность хранилища."""
    s3_host = os.getenv("GARAGE_HOST", "localhost")
    s3_port = int(os.getenv("GARAGE_S3_PORT", "3900"))
    s3_secure = os.getenv("GARAGE_S3_SECURE", "false").lower() == "true"
    bucket_name = os.getenv("GARAGE_BUCKET", "videos")
    
    print(f"Проверка хранилища: {s3_host}:{s3_port}, бакет: {bucket_name}")
    
    # Ожидание готовности хранилища
    if not wait_for_storage(s3_host, s3_port, s3_secure):
        print(f"Ошибка: Хранилище недоступно по адресу {s3_host}:{s3_port}")
        return False
    
    print(f"Хранилище доступно! Бакет '{bucket_name}' будет создан автоматически при первой загрузке.")
    return True


if __name__ == "__main__":
    result = asyncio.run(ensure_storage_available())
    sys.exit(0 if result else 1)
