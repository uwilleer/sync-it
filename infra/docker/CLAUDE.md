# infra/docker

Docker Compose конфигурация монорепозитория. Использует extends-паттерн.

## Структура

```
docker-compose.yml      — корневой файл, extends из подкаталогов
docker-compose.dev.yml  — dev override: build из исходников, volume mount, hot reload
<service>/
  docker-compose.yml    — определение сервиса (image, env, healthcheck, networks)
```

## Extends-паттерн

Корневой `docker-compose.yml` только расширяет сервисы:
```yaml
vacancy-parser:
  extends:
    service: vacancy-parser
    file: vacancy-parser/docker-compose.yml
```

Каждый сервис-файл содержит image, environment, healthcheck, networks.

## Docker Compose сервисы

| Контейнер | Описание |
|-----------|----------|
| postgres | PostgreSQL с healthcheck |
| pgbouncer | connection pooler, depends_on postgres |
| redis | брокер Celery + кэш |
| api-gateway | FastAPI gateway |
| gpt-api | LLM completions |
| scraper-api | Telegram + Habr парсинг |
| telegram-bot | aiogram бот |
| telegram-bot-worker | Celery worker для бота |
| vacancy-parser | FastAPI + источник вакансий |
| vacancy-parser-worker | Celery worker |
| vacancy-parser-beat | Celery Beat (расписание каждые 10 мин) |
| vacancy-processor | FastAPI + обработка вакансий |
| vacancy-processor-worker | Celery worker |
| vacancy-processor-beat | Celery Beat (расписание каждые 5 мин) |
| vacancy-matcher | Go HTTP сервис матчинга |

## Migrator profile

Сервисы `*-migrator` запускаются только с `--profile migrator` для прогона Alembic миграций:
```bash
docker compose --profile migrator up vacancy-parser-migrator
```
Это эквивалентно `make migrate s=vacancy-parser`.

## Dev-режим

`ENV_MODE=development` активирует `docker-compose.dev.yml`:
- x-anchor паттерны (`&build-common`, `&service-common`) для DRY конфигурации
- `build: context: ...` вместо `image:`
- volume mount исходников для hot reload (uvicorn reload / Air)

## Команды

```bash
make up                    # поднять все сервисы
make up s=vacancy-parser   # поднять конкретный сервис
make down                  # остановить и удалить
make stop s=api-gateway    # остановить без удаления
```
