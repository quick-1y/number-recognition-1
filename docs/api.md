# API и авторизация (шаг 8)

## Основные сущности
- **Аутентификация:** OAuth2 password flow, JWT в заголовке `Authorization: Bearer <token>`.
- **Роли:** `admin`, `operator`, `viewer`. Мутации доступны `operator`/`admin`, чтение — с `viewer` и выше.

## Получение токена и профиль
- `POST /api/v1/auth/token` — получить `access_token` (поля `username`, `password` в `application/x-www-form-urlencoded`).
- `GET /api/v1/auth/me` — информация о текущем пользователе и его роли.

## Ingest и конвейер
- `POST /api/v1/ingest/channels` (operator/admin) — зарегистрировать канал.
- `GET /api/v1/ingest/channels` (viewer) — снимок состояния ingest.
- `GET /api/v1/pipeline/status` (viewer) — конфигурация детекции/трекера/OCR/постпроцессинга.

## Списки и правила
- `POST /api/v1/lists` (operator/admin) — создать список.
- `POST /api/v1/lists/{id}/items` (operator/admin) — добавить элемент.
- `GET /api/v1/lists` (viewer) — текущее состояние списков.
- `POST /api/v1/rules` (operator/admin) — зарегистрировать правило IF→THEN.
- `GET /api/v1/rules/status` (viewer) — статус Rules Engine.

## События, webhooks и реле
- `POST /api/v1/events` (operator/admin) — записать событие распознавания.
- `GET /api/v1/events` (viewer) — последние события с фильтрами `plate`, `channel_id`, `limit`.
- `GET /api/v1/events/status` (viewer) — статус Event Manager/Webhook/Relay.
- `POST /api/v1/webhooks/subscriptions` (operator/admin) — зарегистрировать подписку.
- `GET /api/v1/webhooks/subscriptions` (viewer) — активные подписки.
- `POST /api/v1/alarms/relays` (operator/admin) — добавить реле камеры.
- `GET /api/v1/alarms/relays` (viewer) — список реле.
- `POST /api/v1/alarms/relays/{id}/trigger` (operator/admin) — тестовая сработка.

## Заметки по аудиту и TLS
- Все чувствительные вызовы требуют JWT; для production включить TLS терминацию (Ingress/Reverse proxy).
- Для аудита изменений настроек фиксируйте операции на уровне БД или middleware (запланировано в следующих шагах).
