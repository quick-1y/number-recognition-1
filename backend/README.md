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

## Ближайшие доработки
- Шаг 4–5: декодер/детектор/трекер/OCR и сервис очередей при необходимости.
- Шаг 6–8: правила, списки, вебхуки, реле, API для управления.
- Шаг 9: интеграция с фронтендом и ролевой моделью (RBAC).
