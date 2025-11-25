# Инфраструктура хранения и конфигурации

Документ фиксирует минимальные схемы данных и настройки окружения для шага 2.

## PostgreSQL: основные таблицы

| Таблица | Ключевые поля | Описание |
| --- | --- | --- |
| `channels` | `id (uuid, pk)`, `name`, `rtsp_url`, `status`, `roi`, `direction`, `created_at`, `updated_at` | Каналы видеовходов и их настройки (ROI, направление движения, статус подключения). |
| `plate_lists` | `id (uuid, pk)`, `name`, `type (white/black/info)`, `priority`, `schedule`, `ttl`, `created_by`, `created_at`, `updated_at` | Списки номеров с приоритетами и расписаниями активности. |
| `plate_list_items` | `id (uuid, pk)`, `list_id (fk)`, `plate_mask`, `comment`, `expires_at`, `created_at`, `updated_at` | Элементы списков: номер или маска с необязательным TTL. |
| `recognitions` | `id (uuid, pk)`, `channel_id (fk)`, `track_id`, `plate`, `confidence`, `country_pattern`, `bbox`, `direction`, `best_frame_ts`, `meta`, `image_url`, `created_at` | События распознавания с метаданными и ссылкой на изображение. |
| `webhook_subscriptions` | `id (uuid, pk)`, `name`, `url`, `secret`, `is_active`, `filters`, `created_at`, `updated_at` | Подписки на события с фильтрами и секретом для HMAC. |
| `webhook_deliveries` | `id (uuid, pk)`, `subscription_id (fk)`, `event_id (fk)`, `status`, `attempts`, `next_retry_at`, `response_code`, `response_body`, `created_at`, `updated_at` | Лог отправок webhook с количеством попыток и статусом. |
| `users` | `id (uuid, pk)`, `email`, `password_hash`, `role (admin/operator/viewer)`, `is_active`, `created_at`, `updated_at`, `last_login_at` | Пользователи системы, роли и статус. |
| `audit_log` | `id (uuid, pk)`, `actor_id (fk users)`, `action`, `target`, `payload`, `ip`, `created_at` | Аудит изменений настроек и управленческих действий. |

Дополнительно планируются вспомогательные таблицы для хранения параметров расписаний, шаблонов стран и истории статусов каналов.

## Объектное хранилище (S3/MinIO)

- Бакет `plates-events` (по умолчанию) для сохранения изображений и видеоклипов.
- Пути хранения: `channel_id/YYYY/MM/DD/{event_id}/best.jpg`, опционально `clip.mp4` для N секунд до/после события.
- Настройка TTL хранения через политику жизненного цикла бакета или крон-задачу.
- Временные ссылки для UI/API выдаются через pre-signed URL с ограниченным временем действия.

## Переменные окружения (шаблон .env)

| Переменная | Назначение |
| --- | --- |
| `APP_ENV` | `development`/`production` для выбора профиля. |
| `DATABASE_URL` | Строка подключения PostgreSQL в формате `postgresql+psycopg://user:pass@host:port/db`. |
| `S3_ENDPOINT` | Эндпоинт MinIO/S3 (например, `http://localhost:9000`). |
| `S3_REGION` | Регион (может быть пустым для MinIO). |
| `S3_ACCESS_KEY` | Ключ доступа к S3. |
| `S3_SECRET_KEY` | Секретный ключ доступа к S3. |
| `S3_BUCKET` | Название бакета для изображений/клипов. |
| `JWT_SECRET` | Секрет для подписи JWT. |
| `JWT_EXPIRES_MINUTES` | Время жизни токена (в минутах). |
| `API_RATE_LIMIT` | Ограничение на запросы (при необходимости). |
| `LOG_LEVEL` | `INFO`/`DEBUG`/`WARNING` и т.п. |

### Рекомендации по миграциям
- Использовать Alembic для версионирования схемы PostgreSQL; базовые миграции создают таблицы из раздела выше.
- Конфигурацию Alembic хранить в `backend/alembic.ini` (будет добавлено в следующих шагах).
- Для локальной разработки использовать Docker Compose с PostgreSQL и MinIO (появится после фиксации схем).
