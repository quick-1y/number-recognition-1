# Number Recognition

## Описание проекта

**Number Recognition** — это сервис для распознавания номеров автомобилей с использованием видеопотока. Система включает в себя следующие основные компоненты:
- Веб-интерфейс для администрирования и мониторинга.
- API для интеграции с внешними системами.
- Система детекции, трекинга и оптического распознавания символов (OCR).
- Механизмы для фильтрации и нормализации данных.

## Архитектура

Проект включает несколько ключевых частей:
1. **Backend**: FastAPI приложение, отвечающее за API, управление пользователями, обработку видеопотока и события.
2. **Frontend**: Веб-интерфейс на React + Vite, предназначенный для работы с администратором и операторами.
3. **Хранение данных**: SQLite для локальных данных и MinIO для хранения изображений/видеоклипов.

## Зависимости

- **Backend**: Python 3.9+, FastAPI, Alembic, Uvicorn
- **Frontend**: Node.js 20+, npm 9+
- **База данных**: SQLite, MinIO (локальный S3)
- **Прочее**: Docker, Kubernetes (не используется), Prometheus для мониторинга

## Установка и настройка

### Быстрый старт (для разработки)

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/yourrepo/number-recognition.git
    cd number-recognition
    ```

2. Скопируйте шаблон окружения и настройте значения:
    ```bash
    cp .env.example .env
    ```

3. Установите зависимости для **backend**:
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .\.venv\Scripts\Activate.ps1  # Windows (PowerShell)
    pip install -r requirements.txt
    ```

4. Примените миграции Alembic для базы данных:
    ```bash
    alembic upgrade head
    ```

5. Запустите backend:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

6. Установите зависимости для **frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev -- --host --port 5173  # http://localhost:5173
    ```

### Docker

1. Соберите образы:
    ```bash
    docker build -t number-recognition-backend ./backend
    docker build -t number-recognition-frontend ./frontend
    ```

2. Запустите MinIO для локального хранилища S3:
    ```bash
    docker run -d --name number-minio \
        -p 9000:9000 -p 9001:9001 \
        -e MINIO_ACCESS_KEY=minio -e MINIO_SECRET_KEY=minio123 \
        -v $(pwd)/minio-data:/data \
        quay.io/minio/minio:RELEASE.2024-06-13T22-53-53Z server /data --console-address ":9001"
    ```

3. Запустите **backend** со встроенной SQLite:
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

4. Запустите **frontend**, указав URL API:
    ```bash
    docker run -d --name number-frontend -p 5173:80 \
        -e VITE_API_BASE_URL=http://localhost:8000 \
        number-recognition-frontend
    ```

### Регистрация тестового канала (ingest)

1. Получите токен:
    ```bash
    export TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/token \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin@example.com&password=admin123" | jq -r .access_token)
    ```

2. Зарегистрируйте канал:
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

### Проверка состояния детектора/трекера/OCR

1. Проверьте статус:
    ```bash
    curl http://localhost:8000/api/v1/pipeline/status \
        -H "Authorization: Bearer $TOKEN" | jq
    ```

### Работа с событиями

1. Создайте правило для списка номеров:
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
    ```

2. Создайте правило:
    ```bash
    curl -X POST http://localhost:8000/api/v1/rules \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{
          "name": "VIP open gate",
          "conditions": {"list_type": "white", "min_confidence": 0.7, "anti_flood_seconds": 30},
          "actions": {"trigger_relay": true, "send_webhook": true, "annotate_ui": true}
        }'
    ```

### Запись события распознавания

1. Запишите событие:
    ```bash
    curl -X POST http://localhost:8000/api/v1/events \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"channel_id":"demo-rtsp","plate":"A123BC77","confidence":0.8,"direction":"any","image_url":"s3://plates-events/demo/best.jpg"}'
    ```

2. Проверка статуса:
    ```bash
    curl http://localhost:8000/api/v1/events/status \
        -H "Authorization: Bearer $TOKEN" | jq
    ```

### Мониторинг и диагностика

1. Получите метрики:
    ```bash
    curl http://localhost:8000/metrics  # формат Prometheus
    ```

2. Статус мониторинга:
    ```bash
    curl http://localhost:8000/api/v1/monitoring/status -H "Authorization: Bearer $TOKEN" | jq
    ```

## Развёртывание

1. Для развёртывания с Docker Compose:
    ```bash
    docker compose up --build
    ```

2. Если требуется обновление, выполните:
    ```bash
    docker compose build --no-cache && docker compose up
    ```

## Примечания

- Документация по архитектуре, хранилищам, детекции, событиям и другим аспектам находится в директориях `docs/`.
- Все шаги тестирования, настройки и эксплуатации описаны в `README` и в документации в разделе `docs/`.
