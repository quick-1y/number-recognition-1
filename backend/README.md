# Backend (FastAPI)

Базовый каркас сервиса. Реализация функций будет добавляться по шагам дорожной карты.

## Структура
- `app/main.py` — создание FastAPI приложения, базовые пробные эндпоинты и подключение маршрутов.
- `app/api/` — маршруты API v1.
- `app/core/config.py` — конфигурация через переменные окружения (Pydantic BaseSettings).
- `app/db/` — декларативные модели SQLAlchemy, базовый session factory.
- `alembic/` — конфигурация и миграции базы данных.
- `requirements.txt` — зависимости FastAPI, SQLAlchemy и Alembic.

## Быстрый старт (dev)
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env  # при необходимости обновите значения
alembic upgrade head         # применить миграции (требуется доступ к БД из DATABASE_URL)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Работа с миграциями
- Редактируйте модели в `app/db/models.py`.
- Генерация миграции: `alembic revision --autogenerate -m "message"`.
- Применение миграций: `alembic upgrade head`.
- Откат: `alembic downgrade -1`.

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

## Ближайшие доработки
- Шаг 7–8: сервис событий, вебхуки, реле и полнофункциональный REST API с авторизацией.
- Шаг 9: интеграция с фронтендом и ролевой моделью (RBAC).
