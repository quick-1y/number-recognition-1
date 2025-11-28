# Frontend (React + Vite)

Веб-интерфейс для администратора и оператора (шаг 9). Используется React + Vite + TypeScript без UI-фреймворков для лёгкости старт
а.

## Структура
- `src/` — исходники интерфейса.
- `src/components/` — карточки каналов, таблицы событий, формы поиска/списков/настроек/диагностики.
- `src/hooks/` — вспомогательные хуки (например, сохранение JWT + роли).
- `src/styles.css` — базовые стили и сетка.
- `vite.config.ts`, `tsconfig.json` — конфигурация сборки и TypeScript.

## Быстрый старт и установка
- Общие требования: Node.js 20+ (или LTS 18+), npm 9+, открытый порт 5173.
- Убедитесь, что в терминале доступен `node -v` и `npm -v`. Если версии ниже — обновите Node.js с https://nodejs.org.

### Windows (PowerShell)
```powershell
# Разрешить скрипты только на текущую сессию (для активации npm-хуков)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

cd frontend
npm install
npm run dev -- --host --port 5173   # http://localhost:5173
```
Если видите ошибки прав или кеша, очистите: `npm cache clean --force`, затем повторите `npm install`.

### Linux/macOS
```bash
cd frontend
npm install
npm run dev -- --host --port 5173   # http://localhost:5173
```
При конфликтах порта запустите `npm run dev -- --host --port 5174` и откройте указанный адрес.

### Docker
```bash
docker build -t number-recognition-frontend ./frontend
docker run -d --name number-frontend -p 5173:80 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  number-recognition-frontend
```

Переменная окружения для разработки:
- `VITE_API_BASE_URL` — адрес backend (можно задать в `.env` или при запуске Docker).

## Текущая функциональность
- Сетка каналов с выбором раскладки: 1×1, 1×2, 2×2, 2×3, 3×3.
- Вкладки «События», «Поиск», «Списки», «Настройки», «Диагностика» с типовыми элементами UI из ТЗ.
- Маскирование номеров для роли `viewer` (переключатель в панели авторизации).
- Хранение JWT и выбранной роли в localStorage через простой хук.

## Следующие шаги
- Подключить реальные вызовы API (auth, события, списки, поиск) через axios-клиент.
- Добавить загрузку данных каналов/диагностики из backend + realtime обновления.
- Включить экспорты (CSV/JSON/PDF) и отрисовку клипов/изображений по URL S3.
