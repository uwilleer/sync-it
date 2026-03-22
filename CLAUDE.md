# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sync-it — монорепозиторий микросервисной системы парсинга, анализа и матчинга вакансий. Python 3.13.4, один Go-сервис, uv workspace, Docker Compose, PostgreSQL, Redis, Celery.

## Commands

```bash
# Зависимости
make venv-local                        # uv sync --frozen --all-packages --all-groups
make add p=<package> s=<service>       # добавить зависимость в сервис

# Lint
make lint                              # ruff check + ruff format --check + isort --check-only + mypy
make lint-fix                          # ruff format + isort + mypy (автофикс)

# Docker
make up [s=<service>]                  # docker compose up -d --wait
make down [s=<service>]                # docker compose down
make stop [s=<service>]                # docker compose stop

# Миграции (alembic через Docker)
make mm s=<service> m="message"        # создать миграцию
make migrate [s=<service>]             # применить миграции (все или конкретный сервис)
make downgrade s=<service> r=<rev>     # откат миграции
```

ENV_MODE=development включает docker-compose.dev.yml (сборка из исходников, volume-монтирование, hot reload).

## Architecture

### Workspace Layout

- `services/` — микросервисы (каждый — отдельный uv workspace member)
- `libs/common/` — общие библиотеки (тоже workspace members)
- `infra/docker/` — Docker Compose конфигурация (extends-паттерн: каждый сервис имеет свой docker-compose.yml)
- Корневой `pyproject.toml` — workspace root с ruff/mypy/isort конфигурацией

### Services

| Сервис | Стек | Назначение |
|--------|------|------------|
| api-gateway | FastAPI | Прокси-шлюз, маршрутизация через ServiceEnum, API key авторизация |
| gpt-api | FastAPI | Обработка текстов через LLM |
| scraper-api | FastAPI | Парсинг Telegram/Habr API |
| telegram-bot | aiogram | Telegram-бот |
| vacancy-parser | FastAPI + Celery | Парсинг вакансий (HH, Telegram, Habr), Celery Beat расписание |
| vacancy-processor | FastAPI + Celery | Анализ, фильтрация, дедупликация вакансий |
| vacancy-matcher | **Go** (GORM, Air) | Матчинг вакансий, отдельный от uv workspace |

### Shared Libraries (libs/common/)

| Библиотека | Назначение |
|------------|------------|
| database | DatabaseConfig (Pydantic), async SQLAlchemy engine с asyncpg |
| environment | Переменные окружения, enums |
| logger | Фабрика логгеров, подавление шумных библиотек (httpcore, httpx, uvicorn, telethon) |
| redis | Async/sync Redis клиенты, декораторы @singleton и @cache |
| gateway | ServiceEnum маршрутизация |
| sentry | Sentry инициализация с CeleryIntegration |
| shared | BaseRepository, BaseUnitOfWork, LoggingMiddleware, HTTP exception handler |

### Key Patterns

**UnitOfWork** (`libs/common/shared/unitofwork.py`): Async context manager для транзакций. Сервисы наследуют BaseUnitOfWork, определяя свои репозитории. Паттерн использования:
```python
async with UnitOfWork() as uow:
    service = Service(uow)
    await uow.commit()
```

**Celery**: vacancy-parser использует Celery Beat + @singleton декоратор (Redis lock) для периодических задач парсинга.

**Alembic**: Каждый сервис с миграциями имеет свой database/migrations/ с async env.py. Схемы изолированы по сервисам (include_object callback). Модели импортируются динамически через importlib.

**Docker Compose**: extends-паттерн — основной `docker-compose.yml` расширяет отдельные файлы из `infra/docker/<service>/docker-compose.yml`. Dev-файл использует x-anchor паттерны (&service-common, &build-common).

**Dockerfiles (Python)**: Multi-stage — base → builder → deps-dev/deps-prod → source → development/production. Используют uv для зависимостей.

**Go (vacancy-matcher)**: Multi-stage Docker, Air для hot reload в dev, GORM + PostgreSQL, запросы к схеме vacancy_processor.

### Infrastructure

- PostgreSQL через pgbouncer (connection pooling)
- Redis — брокер Celery + кэш
- CI/CD: GitHub Actions — lint, build (matrix по 7 сервисам, Docker buildx с registry cache), deploy через SSH
- Telegram-нотификации о сбоях CI
