# Сервис событий и уведомлений (шаг 7)

Этот документ фиксирует заготовку Event Manager, Webhook Service и Alarm Relay Controller.
Компоненты реализованы как in-memory сервисы с конфигурацией через переменные окружения,
готовые к интеграции с БД/S3 и будущей доставкой уведомлений.

## Event Manager
- Запись события распознавания: `POST /api/v1/events`.
- Содержимое: канал, track_id, номер, уверенность, шаблон страны, bbox, направление,
  ссылка на изображение, произвольные метаданные.
- Настройки хранения (S3/MinIO) подтягиваются из `.env`:
  - `EVENTS_S3_PREFIX` — префикс путей (`events` по умолчанию).
  - `EVENTS_IMAGE_TTL_DAYS` — TTL изображений в днях.
  - `EVENTS_CLIP_BEFORE_SECONDS` / `EVENTS_CLIP_AFTER_SECONDS` — отступы для клипов.
- Статус сервиса: `GET /api/v1/events/status` (блок `events`).

## Webhook Service
- Регистрация подписки: `POST /api/v1/webhooks/subscriptions` (`name`, `url`, `secret`, `filters`).
- Просмотр подписок: `GET /api/v1/webhooks/subscriptions`.
- Настройки повторов и подписи:
  - `WEBHOOK_MAX_ATTEMPTS` — максимум попыток (по умолчанию 5).
  - `WEBHOOK_BACKOFF_SECONDS` — базовый backoff (по умолчанию 30 секунд).
  - `WEBHOOK_SIGNATURE_HEADER` — HTTP-заголовок для HMAC подписи.
- Статус сервиса доступен через `GET /api/v1/events/status` (блок `webhooks`).

## Alarm Relay Controller
- Регистрация реле: `POST /api/v1/alarms/relays` (`name`, `channel_id`, `mode`, `delay_ms`, `debounce_ms`).
- Перечень реле: `GET /api/v1/alarms/relays`.
- Сработка реле: `POST /api/v1/alarms/relays/{relay_id}/trigger`.
- Настройки по умолчанию:
  - `ALARM_RELAY_DEFAULT_MODE` — базовый режим реле (toggle, close_open, open_close, hold_close, hold_open).
  - `ALARM_RELAY_DEBOUNCE_MS` — антидребезг.
- Статус контроллера доступен через `GET /api/v1/events/status` (блок `alarm_relays`).

## База данных и миграции
- Добавлены таблицы `recognitions`, `webhook_subscriptions`, `webhook_deliveries`, `alarm_relays`.
- Миграция: `alembic upgrade head` применит `0004_add_events_and_notifications`.

## Быстрые примеры запросов
```bash
# Записать событие распознавания
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "demo-rtsp",
    "track_id": "track-1",
    "plate": "A123BC77",
    "confidence": 0.82,
    "country": "ru",
    "bbox": [0.1,0.2,0.3,0.4],
    "direction": "any",
    "image_url": "s3://plates-events/demo/best.jpg",
    "meta": {"source": "unit-test"}
  }'

# Зарегистрировать webhook подписку
curl -X POST http://localhost:8000/api/v1/webhooks/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","url":"http://localhost:9000/hook","secret":"abc","filters":{"list":"white"}}'

# Добавить реле и сработать
curl -X POST http://localhost:8000/api/v1/alarms/relays \
  -H "Content-Type: application/json" \
  -d '{"name":"gate-relay","channel_id":"demo-rtsp","mode":"close_open","delay_ms":150}'

curl -X POST http://localhost:8000/api/v1/alarms/relays/{relay_id}/trigger
```
