# Развёртывание (шаг 11)

## Docker Compose
1. Скопируйте `.env.example` в `.env` и при необходимости задайте креды БД/S3.
2. Запустите стэк: `docker compose up --build`.
3. Сервисы:
   - backend: http://localhost:8000 (FastAPI, `/metrics`, `/ready`, `/live`).
   - frontend: http://localhost:5173 (Nginx со статикой Vite-билда).
   - postgres: порт 5432, креды в docker-compose.yml.
   - minio: http://localhost:9000 (консоль http://localhost:9001).

## Kubernetes (каркас)
- Рекомендуется использовать nvidia-container-runtime для GPU узлов.
- Главные манифесты:
  - Deployment/Service backend с переменными окружения из Secret/ConfigMap.
  - Deployment frontend, отдающий статику через Nginx/Ingress.
  - StatefulSet postgres с PVC, StatefulSet MinIO (Standalone) с PVC.
  - ServiceMonitor/PodMonitor для `/metrics` (Prometheus Operator) и Dashboards Grafana.
- Минимальные требования: 1 GPU на 8 каналов, целевой FPS 12+, задержка события ≤500 мс.

## Производственные параметры
- Тюнинг окружения:
  - `INGEST_DEFAULT_TARGET_FPS`, `DETECTOR_DEVICE`, `TRACKER_*` — баланс производительности/качества.
  - `EVENTS_IMAGE_TTL_DAYS` — срок хранения снимков, минимум 90 дней по ТЗ.
  - `POSTPROCESS_ANTI_DUPLICATE_SECONDS` и `RULES_DEFAULT_ANTI_FLOOD_SECONDS` — защита от дублей/флуда.
  - `LOG_FORMAT=json`, `SENTRY_DSN` — наблюдаемость и аудит.
- TLS/Ingress: включите HTTPS на уровне ingress-контроллера или реверс-прокси.

## Непрерывная интеграция
- Проверки: `alembic upgrade --sql` для валидации миграций, линт (ruff/flake8), сборка Docker образов backend/frontend.
- Публикация образов в registry, helm-chart с зависимостями (PostgreSQL, MinIO), values для GPU/CPU профилей.
