# MinIO HTML form upload fix and production testing

**Session ID:** ses_e2ffe93a2ffelePfR6Sr36USQK
**Created:** 11/12/2026, 4:45:16 PM
**Updated:** 11/12/2026, 4:46:19 PM

---

## User

Plan file: D:\IT\New_dev\my_tube_2\.gigacode_vsc\plans\1794487807850-crisp-wizard.md
Read this file first and treat it as the source of truth for implementation.

Implement the following plan:

## Итоги проверки

### Найденные и исправленные проблемы

**1. Подключение к MinIO в production** — уже исправлено ранее:
- `docker-compose.production.yaml`: добавлено `MINIO_HOST=minio`

**2. Загрузка видео через HTML-форму** — исправлено сейчас:
- `app/api/pages/video_pages.py`, строка 140: добавлен параметр `size=file_size` в вызов `upload_video_file()`
- Без этого MinIO SDK выдавал ошибку: `valid part size must be provided when object size is unknown`

### Результат тестирования

Halloween.mp4 (7.61 MB) успешно загружен через HTML-форму `/upload` и доступен для просмотра:

| Шаг | Статус |
|-----|--------|
| Логин | ✅ 200 |
| Открыть /upload | ✅ 200 |
| Загрузка через HTML форму | ✅ 302 → `/video/4?success=Видео успешно загружено!` |
| Страница просмотра /video/4 | ✅ 200 |
| Прямой доступ к файлу | ✅ 200, video/mp4, 7.61 MB |

### Что осталось проверить при необходимости

- **Bucket policy** — ставится автоматически при первой загрузке. Если бакет пустой и пользователь пытается получить видео до первой загрузки — будет 403.
- **MINIO_PUBLIC_URL** — сейчас `http://localhost:9000`. Если приложение на удалённом сервере — нужно изменить на публичный адрес storage.

## Handover from Planning Session

## Discoveries

**1. HTML upload vs API upload discrepancy:**
- `app/api/videos.py` (API endpoint) correctly passes `size=file_size` to `upload_video_file()`
- `app/api/pages/video_pages.py` (HTML form handler) was missing the `size` parameter, causing MinIO SDK error: `"valid part size must be provided when object size is unknown"`
- This is a classic copy-paste divergence: the API endpoint was correct from the start, only the HTML handler was broken

**2. Bucket policy race condition:**
- `minio-init` creates the `videos` bucket via Bitnami minio-client but doesn't set bucket policy
- `app/storage/minio.py` only sets public policy when `make_bucket()` is called (first upload when bucket doesn't exist)
- If bucket exists before first upload, policy is set on first successful upload — subsequent uploads work fine
- The first video after a fresh deploy will return 403 from MinIO directly until policy is applied

**3. Environment variable pattern:**
- `MINIO_HOST` is set directly in compose YAML (not in `.env`) — follows existing project convention
- `.env.production` intentionally doesn't contain `MINIO_HOST` — it's a Docker-internal variable only

## Relevant Files

- `D:\IT\New_dev\my_tube_2\docker-compose.production.yaml` — line 122: `MINIO_HOST=minio` added
- `D:\IT\New_dev\my_tube_2\app\api\pages\video_pages.py` — line 140: `size=file_size` parameter added
- `D:\IT\New_dev\my_tube_2\app\services\video.py` — `upload_video_file()` signature accepts `size: int = 0`
- `D:\IT\New_dev\my_tube_2\app\storage\minio.py` — `Minio()` client creation, bucket policy logic in `upload()`
- `D:\IT\New_dev\my_tube_2\app\core\config.py` — `minio_host` default `"localhost"`, `minio_endpoint` property
- `D:\IT\New_dev\my_tube_2\app\templates\upload.html` — HTML form for video upload
- `D:\IT\New_dev\my_tube_2\Halloween.mp4` — test video file (7.61 MB)

## Implementation Notes

- **No remaining blockers** — both fixes verified working via test script
- **Bucket policy** is a soft issue: it self-heals after first successful upload. Consider adding policy check in `minio-init` or `MinIOStorage.__init__` if you want it fixed proactively
- **MINIO_PUBLIC_URL** left as `http://localhost:9000` — will break if app is accessed from a different machine. Change to public storage URL if deploying remotely
- Docker volumes preserved during testing — no data loss
- All existing functionality (registration, login, channel creation, API upload, HTML upload, video viewing) verified working after fixes

---

## Assistant





**Tool: read**

---

## Assistant



План описывает уже реализованные исправления. Проверю текущее состояние файлов.




**Tool: grep**

**Tool: read**

---

## Assistant



Все исправления из плана уже применены и подтверждены:

| Исправление | Файл | Статус |
|---|---|---|
| `MINIO_HOST=minio` | `docker-compose.production.yaml:122` | ✅ Применено |
| `MINIO_HOST=minio` | `docker-compose.yaml:87` | ✅ Применено |
| `size=file_size` | `app/api/pages/video_pages.py:141` | ✅ Применено |

Оставшиеся моменты из плана — это известные ограничения, не блокирующие работу:

- **Bucket policy** — устанавливается при первой успешной загрузке видео. Первый видео после деплоя может вернуть 403, последующие — работают.
- **MINIO_PUBLIC_URL=http://localhost:9000** — корректно для локального деплоя. При удалённом размещении нужно заменить на публичный адрес storage.

Дополнительных действий не требуется.

---

