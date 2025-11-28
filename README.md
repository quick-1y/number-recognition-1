# Number Recognition Roadmap

Пошаговый план реализации системы автоматического распознавания и обработки автомобильных номеров согласно ТЗ. После завершения
каждого шага статус должен обновляться в этом документе.

## Статус и шаги

Формирование дорожной карты
  - Сформирована структура шагов по ТЗ, зафиксировано требование обновлять статусы после выполнения.

Базовая архитектура и каркас сервисов
  - Описана целевая архитектура модулей и форматы обмена данными (docs/architecture.md).
  - Подготовлен каркас репозитория: backend (FastAPI) с базовым API/health, frontend (React+Vite) и общие файлы.
  - Определены основные интерфейсы между модулями и входные/выходные структуры событий.

Инфраструктура хранения и конфигурации
  - Спецификация схемы встроенной SQLite-БД и структуры объектного хранилища S3/MinIO (docs/storage.md).
  - Настроены миграции Alembic, базовые модели пользователей и ролей, подключение конфигурации (env, secrets).
  - Добавлены шаблоны переменных окружения (.env.example) и модуль конфигурации backend.

Приём и декодирование видеопотока
  - Добавлен ingest-менеджер и API регистрации каналов с отражением статуса (`/api/v1/ingest/channels`).
  - Описан шаг в `docs/ingest.md`, расширена схема БД (таблица `channels`) и переменные окружения для ingest.

Детекция, трекинг и OCR
  - Закреплены интерфейсы `RecognitionPipeline` с конфигурацией детектора, трекера и OCR.
  - Добавлен эндпоинт `/api/v1/pipeline/status` и документация по параметрам (docs/detection.md).
  - Подготовлены переменные окружения для выбора модели YOLO, трекера и OCR-движка.

Постобработка, шаблоны стран и антидубликаты
  - Добавлен Postprocessor с нормализацией номера, голосованием по символам и проверкой по шаблонам стран.
  - Настроены антидубликаты и фильтр ложных срабатываний через конфигурацию окружения и новый статус эндпоинт.

Правила, списки и сценарии
  - CRUD-заготовки для списков (белый/чёрный/информационный) с TTL, приоритетом и расписаниями, модели и миграции в БД.
  - Rules Engine в виде конфигурируемого сервиса с условиями (списки, канал, время, уверенность, направление, антифлуд) и действиями (реле, webhooks, запись клипа, метки), статусы доступны через API.

Сервис событий и уведомлений
  - Добавлен Event Manager (in-memory) с API записи событий и конфигурацией S3/TTL для изображений/клипов.
  - Webhook Service для регистрации подписок, HMAC подписи и параметров backoff, логирование доставок in-memory.
  - Alarm Relay Controller с режимами реле, задержкой/антидребезгом и API регистрации/сработки реле.
  - Документировано в `docs/events.md`.

API и авторизация
  - REST API покрывает события, поиск, каналы ingest, списки и сценарии, webhooks и реле.
  - Добавлена авторизация JWT (OAuth2 password), RBAC (admin/operator/viewer) и проверки ролей на эндпоинтах.
  - Документирован быстрый путь получения токена и вызова защищённых API.

Веб-интерфейс администратора и оператора
  - Каркас React + Vite + TypeScript с вкладками «Каналы», «События», «Поиск», «Списки», «Настройки», «Диагностика».
  - Сетка каналов с раскладками 1×1, 1×2, 2×2, 2×3, 3×3, маскирование номеров для роли viewer и переключатель в UI.
  - Формы поиска, таблица событий, заглушки списков/настроек, диагностика FPS/задержек/ошибок OCR.
  - Детали реализации UI и план интеграции с backend в `docs/ui.md`.

Мониторинг, логирование и тестирование
    - Добавлены `/metrics` для Prometheus, `/api/v1/monitoring/status` для снимка метрик, JSON-логи и опциональный Sentry.
    - Описаны метрики, тестовые видео и нагрузочные проверки (docs/monitoring.md).

Развёртывание и производственные параметры
    - Docker Compose для backend/frontend/minio со встроенной SQLite-БД внутри backend, Dockerfile для сервисов.
    - Kubernetes не используется; документирован тюнинг производительности и наблюдаемости (docs/deployment.md).

Эксплуатационные сценарии и будущие доработки
    - Примеры сценариев, экспортов и рекомендации по развитию (docs/operations.md).

## Примечания
- Каждый завершённый шаг фиксируется галочкой и кратким итогом в списке выше.
- Изменения в шагах или приоритетах фиксируются в рамках ближайшего обновления README.

## Быстрый старт (dev)
1. Клонируйте репозиторий и перейдите в каталог проекта.
2. Скопируйте шаблон окружения и при необходимости задайте значения (по умолчанию используется встроенная SQLite-БД `./data/number_recognition.db`, внешний PostgreSQL не нужен):
   ```bash
   cp .env.example .env
   ```
3. Запустите backend (БД создастся автоматически в `backend/data/number_recognition.db` после миграции):
   ```bash
   cd backend
   # Создание виртуального окружения
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   # Windows (PowerShell)
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   # Устанавливайте зависимости через интерпретатор, к которому привязано venv,
   # чтобы избежать ошибки "ModuleNotFoundError: No module named 'pydantic_settings'"
   # при запуске `uvicorn`.
   pip install -r requirements.txt            # Linux/macOS
   py -m pip install -r requirements.txt      # Windows (PowerShell)
   alembic upgrade head  # применить миграции в локальную SQLite
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   > Если при запуске `uvicorn` появляется `ModuleNotFoundError: No module named 'pydantic_settings'`,
   > убедитесь, что зависимости установлены именно из виртуального окружения: выполните
   > `py -m pip install -r requirements.txt` в активированном PowerShell и затем повторите запуск.
4. Frontend (шаг 9) — веб-интерфейс администратора/оператора на React + Vite. Ниже приведены подробные инструкции для разных окружений:
   - **Общие требования**: Node.js 20+ (или LTS 18+), npm 9+, свободный порт 5173. Если используете proxy/antivirus, разрешите загрузку пакетов из npm.
   - **Windows (PowerShell)**:
     ```powershell
     # Включите выполнение сценариев только на текущий процесс, чтобы активировать venv/скрипты
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

     cd frontend
     # Устанавливаем зависимости через встроенный npm
     npm install
     # Запускаем dev‑сервер
     npm run dev -- --host --port 5173  # http://localhost:5173
     ```
     Если при установке появляются ошибки прав, запустите PowerShell от имени администратора и удалите кеш: `npm cache clean --force`, затем повторите `npm install`.

   - **Linux/macOS**:
     ```bash
     cd frontend
     npm install
     npm run dev -- --host --port 5173  # http://localhost:5173
     ```
     При отсутствии Node.js установите LTS из https://nodejs.org или через пакетный менеджер (`sudo apt install nodejs npm`, `brew install node`).

   - **WSL 2** (Windows + Ubuntu): устанавливайте Node.js внутри WSL и запускайте `npm run dev -- --host 0.0.0.0 --port 5173`; открывайте в браузере Windows по адресу `http://localhost:5173`.

   - **Docker (frontend отдельно)**:
     ```bash
     # Сборка образа UI
     docker build -t number-recognition-frontend ./frontend

     # Запуск с пробросом API адреса
     docker run -d --name number-frontend -p 5173:80 \
       -e VITE_API_BASE_URL=http://localhost:8000 \
       number-recognition-frontend
     ```

   - **Диагностика типовых проблем**:
     - Ошибка `ERR_OSSL_EVP_UNSUPPORTED` — запустите `export NODE_OPTIONS=--openssl-legacy-provider` (Linux/macOS) или `$env:NODE_OPTIONS="--openssl-legacy-provider"` (PowerShell) перед `npm install`.
     - Конфликт порта 5173 — укажите другой порт: `npm run dev -- --host --port 5174` и откройте соответствующий адрес в браузере.
     - Повреждённые зависимости — удалите `node_modules` и `package-lock.json`, затем повторите `npm install`.
5. Создайте пользователя в БД (например, admin) через Python-скрипт после миграций:
   ```bash
   cd backend
   python - <<'PY'
from passlib.context import CryptContext
from app.db import models
from app.db.session import SessionLocal

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash("admin123")
session = SessionLocal()
user = models.User(email="admin@example.com", full_name="Admin", hashed_password=pwd, role=models.UserRole.admin, is_active=True)
session.add(user)
session.commit()
session.close()
print("Создан пользователь:", user.email)
PY
   ```
6. Получите JWT токен (OAuth2 password flow) и сохраните его в переменную окружения:
   ```bash
   export TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=admin123" | jq -r .access_token)
   ```
7. Регистрация тестового канала ingest (опционально, после запуска backend):
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/channels \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{
       "channel_id": "demo-rtsp",
       "name": "Demo RTSP",
       "source": "rtsp://user:pass@camera/stream",
       "target_fps": 12,
       "reconnect_seconds": 3,
       "decoder_priority": ["nvdec", "vaapi", "cpu"],
       "direction": "any"
     }'
   ```
8. Проверка конфигурации детектора/трекера/OCR (шаг 4):
   ```bash
   curl http://localhost:8000/api/v1/pipeline/status \
     -H "Authorization: Bearer $TOKEN" | jq
   ```
9. В ответе появится блок `postprocess` (шаг 5) с текущими порогами, шаблонами стран и настройками антидубликатов.
10. Создание списка номеров и правила (шаг 6):
   ```bash
   curl -X POST http://localhost:8000/api/v1/lists \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{
       "name": "VIP",
       "type": "white",
       "priority": 10,
       "ttl_seconds": 86400,
       "schedule": {"timezone": "UTC", "ranges": [{"days": [1,2,3,4,5], "from": "08:00", "to": "20:00"}]}
     }'

   curl -X POST http://localhost:8000/api/v1/rules \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{
       "name": "VIP open gate",
       "conditions": {"list_type": "white", "min_confidence": 0.7, "anti_flood_seconds": 30},
       "actions": {"trigger_relay": true, "send_webhook": true, "annotate_ui": true}
     }'
   ```
11. Запись события распознавания и проверка статусов сервисов уведомлений (шаг 7):
   ```bash
   curl -X POST http://localhost:8000/api/v1/events \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"channel_id":"demo-rtsp","plate":"A123BC77","confidence":0.8,"direction":"any","image_url":"s3://plates-events/demo/best.jpg"}'

   curl http://localhost:8000/api/v1/events/status \
     -H "Authorization: Bearer $TOKEN" | jq
   ```
12. Поиск последних событий (шаг 8):
   ```bash
   curl "http://localhost:8000/api/v1/events?plate=A123&limit=5" \
     -H "Authorization: Bearer $TOKEN" | jq
   ```
13. Мониторинг и наблюдаемость (шаг 10):
   ```bash
   curl http://localhost:8000/metrics  # формат Prometheus
   curl http://localhost:8000/api/v1/monitoring/status -H "Authorization: Bearer $TOKEN" | jq
   ```
14. Запуск всего стека через Docker Compose (шаг 11) со встроенной SQLite и MinIO:
   ```bash
   docker compose up --build
   # при изменениях кода: docker compose build --no-cache && docker compose up
   ```

## Запуск в Docker (без Compose)
1. Соберите образы:
   ```bash
   docker build -t number-recognition-backend ./backend
   docker build -t number-recognition-frontend ./frontend
   ```
2. Запустите MinIO (локальный S3):
   ```bash
   docker run -d --name number-minio \
     -p 9000:9000 -p 9001:9001 \
     -e MINIO_ACCESS_KEY=minio -e MINIO_SECRET_KEY=minio123 \
     -v $(pwd)/minio-data:/data \
     quay.io/minio/minio:RELEASE.2024-06-13T22-53-53Z server /data --console-address ":9001"
   ```
3. Запустите backend со встроенной SQLite (файл будет сохранён в `backend/data`):
   ```bash
   mkdir -p backend/data
   docker run -d --name number-backend --env-file .env \
     -e DATABASE_URL=sqlite:////app/data/number_recognition.db \
     -e S3_ENDPOINT=http://number-minio:9000 \
     -e S3_ACCESS_KEY=minio -e S3_SECRET_KEY=minio123 -e S3_BUCKET=plates-events \
     -p 8000:8000 \
     -v $(pwd)/backend/data:/app/data \
     --link number-minio \
     number-recognition-backend
   ```
4. Запустите frontend, указывая URL API:
   ```bash
   docker run -d --name number-frontend -p 5173:80 \
     -e VITE_API_BASE_URL=http://localhost:8000 \
     number-recognition-frontend
   ```
