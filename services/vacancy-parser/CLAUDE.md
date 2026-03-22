# vacancy-parser

FastAPI + Celery Beat сервис парсинга вакансий из HH.ru, Telegram каналов и Habr Career.

## Структура

- `src/main.py` — FastAPI app (API для ручного запуска парсинга)
- `src/celery_app/app.py` — Celery app
- `src/celery_app/beat.py` — расписание: `parse_vacancies` каждые 10 минут
- `src/tasks/vacancies.py` — Celery task `parse_vacancies`: запускает все три парсера параллельно
- `src/parsers/` — `HeadHunterParser`, `TelegramParser`, `HabrParser` (наследуют `base.py`)
- `src/clients/habr/`, `src/clients/telegram/` — HTTP клиенты к scraper-api
- `src/clients/profession.py` — клиент к vacancy-processor для получения списка профессий (фильтр парсинга)
- `src/constants/telegram.py` — список Telegram channel links для парсинга
- `src/constants/fingerprint.py` — логика fingerprint для дедупликации
- `src/database/models/` — `Vacancy` (base, polymorphic) + `HabrVacancy`, `HeadHunterVacancy`, `TelegramVacancy`
- `src/unitofwork.py` — `UnitOfWork` с репозиториями по каждому источнику
- `src/api/v1/vacancies.py` — endpoint получения необработанных вакансий (для vacancy-processor)

## Ключевые паттерны

- `@singleton(timedelta(minutes=60))` — Redis lock предотвращает одновременный запуск нескольких экземпляров задачи
- Вакансии хранятся как `data: Text` (сырой текст) + `fingerprint` (gist trigram index для дедупликации)
- `processed_at IS NULL` — индекс для быстрого получения необработанных вакансий
- Три Docker контейнера: `vacancy-parser` (FastAPI), `vacancy-parser-worker` (Celery), `vacancy-parser-beat` (Beat)
- Polymorphic модель: `Vacancy.source` определяет подкласс (habr / head_hunter / telegram)

## БД схема (схема `vacancy_parser` в PostgreSQL)

- `vacancies` — базовая polymorphic таблица (source, hash, fingerprint, link, data, published_at, processed_at)
- `habr_vacancies`, `head_hunter_vacancies`, `telegram_vacancies` — расширения с source-специфичными полями

## Миграции

```bash
make mm s=vacancy-parser m="message"
make migrate s=vacancy-parser
```

## Зависимости

- Вызывает: scraper-api (Telegram + Habr парсинг), vacancy-processor (список профессий)
- Все запросы через api-gateway
- Redis — брокер Celery
- pgbouncer — PostgreSQL

## Конфигурация

```
ENV_MODE=...
ENV_SERVICE_INTERNAL_HOST=...
ENV_SERVICE_INTERNAL_PORT=...
DATABASE_HOST/PORT/DB/USER/PASSWORD=...
REDIS_DSN=...
HEAD_HUNTER_ACCESS_TOKEN=...
HEAD_HUNTER_APP_NAME=...
HEAD_HUNTER_EMAIL=...
```
