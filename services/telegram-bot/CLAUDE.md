# telegram-bot

aiogram 3 Telegram бот для поиска и матчинга вакансий с профилем пользователя.

## Структура

- `src/main.py` — точка входа, uvloop, polling или webhook в зависимости от `service_config.use_webhook`
- `src/setup/` — `polling.py`, `webhook.py`, `lifespan.py` — режимы запуска бота
- `src/handlers/` — обработчики команд и сообщений
  - `menu.py` — главное меню
  - `preferences.py` — настройки предпочтений (профессии, грейды, форматы)
  - `skills/` — управление навыками (загрузка резюме, извлечение, toggle)
  - `vacancies.py` — просмотр вакансий
  - `faq/` — FAQ
- `src/callbacks/` — inline callback handlers
- `src/keyboard/inline/` и `src/keyboard/reply/` — фабрики клавиатур
- `src/middlewares/` — auth, database session, throttling, logging, reset_state
- `src/tasks/process_resume.py` — Celery task: обработка резюме (PDF/TXT/текст) через gpt-api
- `src/celery_app/app.py` — Celery app (без Beat — задачи запускаются вручную из handlers)
- `src/clients/` — HTTP клиенты к vacancy-processor (grades, profession, skills, work_formats) и vacancy-matcher
- `src/database/models/` — `User`, `UserPreference`
- `src/unitofwork.py` — `UnitOfWork` с репозиториями users и user_preferences
- `src/utils/readers/` — абстракция чтения PDF/TXT файлов
- `src/utils/text_extractor/` — `TextExtractor`: определяет тип файла и читает текст

## Ключевые паттерны

- `UserPreference` хранит выбранные пользователем категории (профессии, навыки, грейды, форматы работы, источники) как пары `(category_code, item_id, item_name)`
- Навыки можно обновить: загрузить резюме (PDF/TXT) или ввести список через запятую (`toggle=True`)
- Celery worker запускается отдельным Docker контейнером `telegram-bot-worker`
- Бот общается с vacancy-processor и vacancy-matcher через api-gateway

## БД схема (схема `public` в PostgreSQL)

- `users` — Telegram users (telegram_id, username, first/last name, created_at, last_active_at)
- `user_preferences` — предпочтения (user_id, category_code, item_id, item_name), unique по (user_id, category_code, item_id)

## Миграции

```bash
make mm s=telegram-bot m="message"
make migrate s=telegram-bot
```

## Зависимости

- Вызывает: vacancy-processor (grades, professions, skills, work_formats), vacancy-matcher (match)
- Все запросы через api-gateway с `X-API-Key`
- Redis — брокер Celery
- pgbouncer — подключение к PostgreSQL

## Конфигурация

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_BOT_USE_WEBHOOK=...
TELEGRAM_BOT_SUPPORT_USERNAME=...
ENV_MODE=...
ENV_SERVICE_INTERNAL_HOST=...
ENV_SERVICE_INTERNAL_PORT=...
DATABASE_HOST/PORT/DB/USER/PASSWORD=...
REDIS_DSN=...
```
