# Backend (FastAPI)

Базовый каркас сервиса. Реализация функций будет добавляться по шагам дорожной карты.

## Структура
- `app/main.py` — создание FastAPI приложения, базовые пробные эндпоинты и подключение маршрутов.
- `app/api/` — маршруты API v1.
- `app/core/config.py` — конфигурация через переменные окружения (Pydantic BaseModel + dotenv).
- `app/db/` — декларативные модели SQLAlchemy, базовый session factory.
- `alembic/` — конфигурация и миграции базы данных.
- `requirements.txt` — зависимости FastAPI, SQLAlchemy и Alembic.

## Быстрый старт (dev)
```
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

   # Устанавливайте зависимости через интерпретатор, к которому привязано venv.
   pip install -r requirements.txt            # Linux/macOS
   py -m pip install -r requirements.txt      # Windows (PowerShell)
cp ../.env.example ../.env  # при необходимости обновите значения
alembic upgrade head         # применить миграции (требуется доступ к БД из DATABASE_URL)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Если при запуске `uvicorn` появляются ошибки валидации настроек, убедитесь, что
> переменные окружения заданы (см. `.env.example`) и команды установки зависимостей
> выполнены из активированного виртуального окружения.

### Работа с миграциями
- Редактируйте модели в `app/db/models.py`.
- Генерация миграции: `alembic revision --autogenerate -m "message"`.
- Применение миграций: `alembic upgrade head`.
- Откат: `alembic downgrade -1`.

#### Локальная БД и бэкапы
- По умолчанию используется SQLite-файл `data/number_recognition.db` в корне репозитория (`DATABASE_URL=sqlite:///./data/number_recognition.db`).
- Alembic и приложение автоматически создают каталог `data/` и сам файл при первом запуске.
- Для резервного копирования достаточно сохранить файл `data/number_recognition.db` (например, скопировать или архивировать каталог `data/`).
- Для восстановления остановите сервис, замените файл из резервной копии и выполните `alembic upgrade head`, чтобы привести схему к актуальной версии миграций.

## Ingest (шаг 3)
- `app/pipeline/ingest_manager.py` хранит конфигурацию каналов, целевой FPS, приоритет декодера и статусы подключений.
- API `/api/v1/ingest/channels` (POST/GET) позволяет зарегистрировать канал и получить снимок состояния ingest.

Пример запроса регистрации канала:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/channels \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "gate-east",
    "name": "Восточный въезд",
    "source": "rtsp://user:pass@camera/stream",
    "protocol": "rtsp",
    "target_fps": 12,
    "reconnect_seconds": 3,
    "decoder_priority": ["nvdec", "vaapi", "cpu"],
    "direction": "any"
  }'
```

## Детекция, трекинг и OCR (шаг 4)
- `app/pipeline/recognition.py` — настройки детектора (YOLOv8/YOLOv11), трекера (ByteTrack/SORT) и OCR.
- Переменные окружения задают выбранные движки, device, пороги и языки (`.env.example`).
- API `/api/v1/pipeline/status` возвращает текущую конфигурацию для диагностики.

## Постобработка и антидубликаты (шаг 5)
- `app/pipeline/postprocess.py` — нормализация номера, посимвольное голосование, коррекция похожих символов, проверка шаблонов стран
  и подавление дубликатов в заданном окне времени.
- Конфигурация через переменные `POSTPROCESS_*` в `.env.example` (пороги, шаблоны стран, окно антидубликатов, минимальное число кадров).
- API `/api/v1/pipeline/status` дополнен блоком `postprocess` для UI/диагностики.

## Правила, списки и сценарии (шаг 6)
- `app/rules/engine.py` — заготовка Rules Engine с условиями (списки, каналы, уверенность, направление, расписания) и действиями
  (реле, webhook, запись клипа, метки).
- API `/api/v1/lists` и `/api/v1/lists/{id}/items` — черновой CRUD списков в памяти (белый/чёрный/информационный).
- API `/api/v1/rules` и `/api/v1/rules/status` — регистрация правил IF→THEN и просмотр текущих условий/действий/списков.
- Переменные `RULES_DEFAULT_*` в `.env.example` — дефолтные пороги уверенности, антифлуд и действия.

## События, webhooks и реле (шаг 7)
- `app/events/__init__.py` — Event Manager (in-memory), Webhook Service и Alarm Relay Controller.
- API `/api/v1/events` и `/api/v1/events/status` — запись события распознавания и снимок статусов (events/webhooks/relays).
- API `/api/v1/webhooks/subscriptions` — регистрация и просмотр подписок с HMAC секретом и настройками повторов.
- API `/api/v1/alarms/relays` и `/api/v1/alarms/relays/{id}/trigger` — управление реле камер и тестовая сработка.
- Новые переменные окружения: `EVENTS_*`, `WEBHOOK_*`, `ALARM_RELAY_*` (см. `.env.example`).

## Авторизация и API (шаг 8)
- `app/core/security.py` — генерация/проверка JWT, bcrypt-хэши паролей.
- `app/api/deps.py` — зависимости FastAPI: получение текущего пользователя, проверка ролей (admin/operator/viewer).
- `/api/v1/auth/token` (OAuth2 password flow) — получение access token; `/api/v1/auth/me` — сведения о текущем пользователе.
- Все mutating endpoints (ingest, lists, rules, events, webhooks, relays) требуют ролей `operator` или `admin`, чтение — `viewer` и выше.
- Пример SQL для создания пользователя в README (секция быстрого старта); используйте bcrypt-хэш пароля.

## Мониторинг, логирование и тестирование (шаг 10)
- `/metrics` — экспорт Prometheus; `/api/v1/monitoring/status` — JSON-снимок.
- `app/monitoring.py` — in-memory registry для счетчиков/гейджей/гистограмм.
- `app/core/logging.py` — JSON-логирование, интеграция с Sentry (опционально).

## Развёртывание (шаг 11)
- Dockerfile для backend, docker-compose.yml поднимает postgres/minio/backend/frontend.
- В Kubernetes подключайте `/metrics` через ServiceMonitor/Prometheus Operator.

## Эксплуатация (шаг 12)
- Экспорт/отчёты по событиям (CSV/JSON/PDF) и расширения (ReID, PTZ) описаны в `docs/operations.md`.
