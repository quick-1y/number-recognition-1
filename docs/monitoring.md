# Мониторинг, логирование и тестирование (шаг 10)

## Метрики
- `/metrics` — экспорт Prometheus (counters/gauges/histograms). Включен по умолчанию (`METRICS_ENABLED=true`).
- `/api/v1/monitoring/status` — JSON-снимок метрик и состояния сервисов.
- Ключевые метрики:
  - `number_recognition_events_total{channel="..."}` — количество событий.
  - `number_recognition_event_confidence_avg` — средний confidence распознанных номеров.
  - `number_recognition_ingest_channels` — активные каналы ingest.
  - `number_recognition_webhook_subscriptions` — количество webhook-подписок.
  - `number_recognition_relay_triggers_total` — количество сработок реле.

## Логирование
- Формат JSON по умолчанию (`LOG_FORMAT=json`, `LOG_LEVEL=INFO`).
- Поддержка Sentry (`SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`).
- Выводится в stdout, совместимо с системами сбора логов в Docker/K8s.

## Health-checks
- `/ready`, `/live` — простые проверки готовности/жизни.
- `/api/v1/health` — health API-слоя.

## Нагрузочные тесты и тестовые видео
- Рекомендуется держать каталог `testdata/videos` с набором дневных/ночных/сложных сцен.
- Пример команды для нагрузочного теста (locust-подход):
  - эмулируйте POST `/api/v1/events` c параметрами `channel_id`, `confidence`, `image_url`.
- Метрики задержки/ошибок доступны через Prometheus; используйте Grafana dashboards на основе этих метрик.

## Диагностика OCR/детектора
- `/api/v1/pipeline/status` возвращает текущую конфигурацию детектора/трекера/OCR/постобработки.
- `/api/v1/events/status` — сводка событий, webhook-доставок и реле.
