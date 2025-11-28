# Развёртывание (шаг 11)

## Docker Compose
1. Скопируйте `.env.example` в `.env`; по умолчанию используется встроенная SQLite-БД (`./data/number_recognition.db`).
2. Запустите стэк: `docker compose up --build` (пересборка без кэша: `docker compose build --no-cache`).
3. Сервисы:
   - backend: http://localhost:8000 (FastAPI, `/metrics`, `/ready`, `/live`), хранит SQLite-файл в volume `backend_data` (`/app/data`).
   - frontend: http://localhost:5173 (Nginx со статикой Vite-билда).
   - minio: http://localhost:9000 (консоль http://localhost:9001).

## Docker (ручной запуск)
- Соберите образы: `docker build -t number-recognition-backend ./backend` и `docker build -t number-recognition-frontend ./frontend`.
- Поднимите MinIO: `docker run -d --name number-minio -p 9000:9000 -p 9001:9001 -e MINIO_ACCESS_KEY=minio -e MINIO_SECRET_KEY=minio123 -v $(pwd)/minio-data:/data quay.io/minio/minio:RELEASE.2024-06-13T22-53-53Z server /data --console-address ":9001"`.
- Backend со встроенной SQLite: `docker run -d --name number-backend --env-file .env -e DATABASE_URL=sqlite:////app/data/number_recognition.db -e S3_ENDPOINT=http://number-minio:9000 -e S3_ACCESS_KEY=minio -e S3_SECRET_KEY=minio123 -e S3_BUCKET=plates-events -p 8000:8000 -v $(pwd)/backend/data:/app/data --link number-minio number-recognition-backend`.
- Frontend: `docker run -d --name number-frontend -p 5173:80 -e VITE_API_BASE_URL=http://localhost:8000 number-recognition-frontend`.

## Kubernetes
Kubernetes в этой поставке не используется; целевой способ развёртывания — Docker/Docker Compose.

## Производственные параметры
- Тюнинг окружения:
  - `INGEST_DEFAULT_TARGET_FPS`, `DETECTOR_DEVICE`, `TRACKER_*` — баланс производительности/качества.
  - `EVENTS_IMAGE_TTL_DAYS` — срок хранения снимков, минимум 90 дней по ТЗ.
  - `POSTPROCESS_ANTI_DUPLICATE_SECONDS` и `RULES_DEFAULT_ANTI_FLOOD_SECONDS` — защита от дублей/флуда.
  - `LOG_FORMAT=json`, `SENTRY_DSN` — наблюдаемость и аудит.
- TLS: включите HTTPS на уровне реверс-прокси перед backend/frontend.

## Непрерывная интеграция
- Проверки: `alembic upgrade --sql` для валидации миграций, линт (ruff/flake8), сборка Docker образов backend/frontend.
- Публикация образов в registry, экспорт актуального docker-compose.yml и переменных для профилей GPU/CPU.
