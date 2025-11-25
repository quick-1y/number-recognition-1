# Number Recognition Roadmap

Пошаговый план реализации системы автоматического распознавания и обработки автомобильных номеров согласно ТЗ. После завершения
каждого шага статус должен обновляться в этом документе.

## Статус и шаги

- [x] Шаг 0: Формирование дорожной карты
  - Сформирована структура шагов по ТЗ, зафиксировано требование обновлять статусы после выполнения.
- [x] Шаг 1: Базовая архитектура и каркас сервисов
  - Описана целевая архитектура модулей и форматы обмена данными (docs/architecture.md).
  - Подготовлен каркас репозитория: backend (FastAPI) с базовым API/health, frontend (React+Vite) и общие файлы.
  - Определены основные интерфейсы между модулями и входные/выходные структуры событий.
- [x] Шаг 2: Инфраструктура хранения и конфигурации
  - Спецификация схемы БД PostgreSQL и структуры объектного хранилища S3/MinIO (docs/storage.md).
  - Настроены миграции Alembic, базовые модели пользователей и ролей, подключение конфигурации (env, secrets).
  - Добавлены шаблоны переменных окружения (.env.example) и модуль конфигурации backend.
- [x] Шаг 3: Приём и декодирование видеопотока
  - Добавлен ingest-менеджер и API регистрации каналов с отражением статуса (`/api/v1/ingest/channels`).
  - Описан шаг в `docs/ingest.md`, расширена схема БД (таблица `channels`) и переменные окружения для ingest.
- [x] Шаг 4: Детекция, трекинг и OCR
  - Закреплены интерфейсы `RecognitionPipeline` с конфигурацией детектора, трекера и OCR.
  - Добавлен эндпоинт `/api/v1/pipeline/status` и документация по параметрам (docs/detection.md).
  - Подготовлены переменные окружения для выбора модели YOLO, трекера и OCR-движка.
- [x] Шаг 5: Постобработка, шаблоны стран и антидубликаты
  - Добавлен Postprocessor с нормализацией номера, голосованием по символам и проверкой по шаблонам стран.
  - Настроены антидубликаты и фильтр ложных срабатываний через конфигурацию окружения и новый статус эндпоинт.
- [x] Шаг 6: Правила, списки и сценарии
  - CRUD-заготовки для списков (белый/чёрный/информационный) с TTL, приоритетом и расписаниями, модели и миграции в БД.
  - Rules Engine в виде конфигурируемого сервиса с условиями (списки, канал, время, уверенность, направление, антифлуд) и действиями (реле, webhooks, запись клипа, метки), статусы доступны через API.
- [x] Шаг 7: Сервис событий и уведомлений
  - Добавлен Event Manager (in-memory) с API записи событий и конфигурацией S3/TTL для изображений/клипов.
  - Webhook Service для регистрации подписок, HMAC подписи и параметров backoff, логирование доставок in-memory.
  - Alarm Relay Controller с режимами реле, задержкой/антидребезгом и API регистрации/сработки реле.
  - Документировано в `docs/events.md`.
- [x] Шаг 8: API и авторизация
  - REST API покрывает события, поиск, каналы ingest, списки и сценарии, webhooks и реле.
  - Добавлена авторизация JWT (OAuth2 password), RBAC (admin/operator/viewer) и проверки ролей на эндпоинтах.
  - Документирован быстрый путь получения токена и вызова защищённых API.
- [ ] Шаг 9: Веб-интерфейс администратора и оператора
  - Сетка каналов (1×1, 1×2, 2×2, 2×3, 3×3), вкладки «События», «Поиск», «Списки», «Настройки», «Диагностика».
  - Маскирование номеров для роли viewer, настройка сроков хранения изображений и экспорта (CSV/JSON/PDF).
  - Диагностика FPS, задержек, ошибок OCR и статусов.
- [ ] Шаг 10: Мониторинг, логирование и тестирование
  - Prometheus метрики (задержка, FPS, ошибки OCR, dropped frames), Grafana dashboard, health-check /ready /live.
  - Логи JSON, интеграция с Sentry (опционально), нагрузочные тесты и тестовые видео (день/ночь/дождь/грязь/засвет).
- [ ] Шаг 11: Развёртывание и производственные параметры
  - Docker Compose, варианты для Kubernetes, поддержка GPU (nvidia-container-runtime).
  - Настройка целевых FPS/задержки, поддержка ≥8 каналов на GPU, хранение событий ≥90 суток, маскирование/хеширование при экспорте.
- [ ] Шаг 12: Эксплуатационные сценарии и будущие доработки
  - Подготовка примеров сценариев и экспорта/отчётов (период, фильтры, каналы).
  - Рекомендации по будущим улучшениям: ReID марки/цвета, двухстрочные номера, PTZ управление.

## Примечания
- Каждый завершённый шаг фиксируется галочкой и кратким итогом в списке выше.
- Изменения в шагах или приоритетах фиксируются в рамках ближайшего обновления README.

## Быстрый старт (dev)
1. Клонируйте репозиторий и перейдите в каталог проекта.
2. Скопируйте шаблон окружения и при необходимости задайте значения (локально достаточно оставить значения по умолчанию):
   ```bash
   cp .env.example .env
   ```
3. Запустите backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head  # применить миграции (требуется доступ к БД)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Frontend будет развёрнут начиная с шага 9 (React + Vite). После инициализации используйте:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Создайте пользователя в БД (например, admin). Пример SQL после применения миграций:
   ```sql
   INSERT INTO users (id, email, full_name, hashed_password, role, is_active)
   VALUES (gen_random_uuid(), 'admin@example.com', 'Admin', '<bcrypt_hash>', 'admin', true);
   -- bcrypt-hash можно сгенерировать так: python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('admin123'))"
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
