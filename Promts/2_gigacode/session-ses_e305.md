# MinIO video upload and playback fix

**Session ID:** ses_e3054db64ffe018Ly7e2SbL3Fs
**Created:** 11/12/2026, 3:11:02 PM
**Updated:** 11/12/2026, 3:13:19 PM

---

## User

Plan file: D:\IT\New_dev\my_tube_2\.gigacode_vsc\plans\1794482168144-eager-engine.md
Read this file first and treat it as the source of truth for implementation.

Implement the following plan:

Готов отчёт. Вот сводка всех исправлений:

---

## Отчёт: Исправление загрузки и просмотра видео через MinIO

### Найденные проблемы и исправления

#### 1. `docker-compose.yaml` — Добавлен сервис MinIO

**Было:** MinIO отсутствовал, использовался `STORAGE_TYPE=filesystem`

**Стало:**
- Добавлен сервис `minio` с образом `dockerhub.timeweb.cloud/bitnamilegacy/minio:latest`
- Добавлен сервис `minio-init` для автоматического создания бакета `videos`
- Изменено `STORAGE_TYPE=minio`
- Добавлены переменные: `MINIO_HOST=minio`, `MINIO_PORT=9000`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET`, `MINIO_PUBLIC_URL`, `MINIO_SECURE=false`
- Добавлена зависимость API от `minio-init`
- Добавлен volume `minio_data`

#### 2. `app/core/config.py` — Добавлен порт MinIO

**Было:** `minio_host: str = "localhost"` — SDK подключался к порту 80 по умолчанию

**Стало:**
- Добавлено поле `minio_port: int = 9000`
- Добавлено свойство `minio_endpoint` — возвращает `host:port` для SDK

#### 3. `app/storage/minio.py` — Исправлен endpoint и политика бакета

**Было:**
- SDK подключался к `localhost:80`
- Политика публичного доступа была закомментирована

**Стало:**
- SDK подключается к `settings.minio_endpoint` (например, `minio:9000`)
- Раскомментирована установка публичной политики бакета (`set_bucket_policy`)
- Добавлен импорт `json`

#### 4. `app/api/videos.py` — Исправлен upload endpoint

**Было:** Параметры `title`, `description`, `privacy` читались из query-строк

**Стало:** Параметры читаются из `Form()` данных

#### 5. `app/services/video.py` — Передан размер файла

**Было:** Размер файла не передавался в `storage.upload()`

**Стало:** Добавлен параметр `size` и передача в `storage.upload(size=size)`

### Результат тестирования

| Шаг | Статус |
|-----|--------|
| Регистрация пользователя | ✅ 201 |
| Создание канала | ✅ 201 |
| Загрузка видео в MinIO | ✅ 201 |
| Доступ к файлу из MinIO | ✅ 200, 7978127 bytes |
| HTML-страница просмотра | ✅ 200, video URL в `<source>` |
| Все контейнеры | ✅ Up и healthy |

### Архитектура видео-потока (рабочая)

```
[Браузер] → POST /upload (port 8000, FastAPI)
  → [API] создаёт запись в БД
  → [API] загружает файл в MinIO (minio:9000)
  → [API] возвращает URL: http://localhost:9000/videos/videos/{id}.mp4

[Браузер] → GET /video/{id} (port 8000, FastAPI)
  → [API] возвращает HTML с <video src="http://localhost:9000/videos/videos/...">

[Браузер] → GET http://localhost:9000/videos/videos/{id}.mp4 (port 9000, MinIO)
  → [MinIO] отдаёт видеофайл напрямую (публичный бакет)
```

## Handover from Planning Session

## Discoveries

1. **MinIO SDK port issue**: The `minio` Python SDK defaults to port 80 when only hostname is provided. The fix required adding `minio_port` to settings and constructing `minio_endpoint` as `host:port` string.

2. **File size is mandatory for MinIO streaming uploads**: `MinIOStorage.upload()` passes `size` parameter to MinIO SDK's `put_object()`. When `size=0` (default), SDK throws `ValueError: valid part size must be provided when object size is unknown` because the file stream's exact size is unknown. The API endpoint already calculated `file_size` but didn't pass it to the service.

3. **Bitnami-specific env vars**: The Bitnami MinIO image uses `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` (not `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` like the official image). The `minio-init` container uses `MINIO_SERVER_HOST`, `MINIO_SERVER_PORT_NUMBER`, etc. — Bitnami wrapper conventions.

4. **Bucket must have public policy for browser playback**: Without `set_bucket_policy` granting `s3:GetObject` to `*`, MinIO returns 403 for direct file access from the browser's `<video>` tag.

## Relevant Files

- `docker-compose.yaml` — Added `minio` and `minio-init` services, changed API to use MinIO storage
- `app/core/config.py` — Added `minio_port` field and `minio_endpoint` property for SDK connection
- `app/storage/minio.py` — Fixed client to use `settings.minio_endpoint` instead of `settings.minio_host`; uncommented `set_bucket_policy` for public access
- `app/api/videos.py` — Changed `upload_video` parameters from query to `Form()`; added `size=file_size` to service call
- `app/services/video.py` — Added `size` parameter to `upload_video_file()` and passes it to `storage.upload()`

## Implementation Notes

1. **Network connectivity**: The API container connects to MinIO via Docker network hostname `minio`, not `localhost`. This is why the endpoint must include the port.

2. **MinIO initialization order**: API depends on `minio-init` which depends on `minio` being healthy. The init container creates the `videos` bucket using Bitnami's minio-client wrapper.

3. **Existing bucket policy**: After first successful upload, the bucket policy is already set. Subsequent redeploys don't need to recreate the policy, but the code should be idempotent.

4. **Test artifacts**: Test videos were uploaded during verification (IDs 3-5 in DB). Clean up test data if needed for fresh testing.

5. **Container restarts**: After code changes, the API image must be rebuilt (`docker compose up -d --build api`) because the entrypoint script runs alembic migrations and seeds data each time.

---

## Assistant





**Tool: read**

---

## Assistant









**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant



Все файлы из плана уже содержат необходимые изменения. Проверяю каждый пункт отчёта:

**1. `docker-compose.yaml`** — сервис MinIO (строки 24-44), minio-init (строки 46-65), `STORAGE_TYPE=minio` (строка 85), все MINIO-переменные (строки 87-93), зависимость от `minio-init` (строки 101-102), volume `minio_data` (строка 109) — всё на месте.

**2. `app/core/config.py`** — поле `minio_port: int = 9000` (строка 58), свойство `minio_endpoint` (строки 61-64) — реализовано.

**3. `app/storage/minio.py`** — SDK подключается к `settings.minio_endpoint` (строка 33), `set_bucket_policy` раскомментирован (строка 78), `json` импортирован (строка 6) — всё на месте.

**4. `app/api/videos.py`** — параметры `title`, `description`, `privacy` читаются из `Form()` (строки 105-107) — исправлено.

**5. `app/services/video.py`** — параметр `size` принят в `upload_video_file` (строка 76) и передан в `storage.upload(size=size)` (строка 100) — реализовано.

Все изменения из плана уже применены ранее. Файлы готовы к сборке и запуску через `docker compose up -d --build`.

---

