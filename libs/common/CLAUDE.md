# libs/common

Общие библиотеки — uv workspace members, подключаемые как зависимости всех Python сервисов.

## Библиотеки

| Директория | Пакет | Назначение |
|------------|-------|------------|
| `database/` | `common-database` | DatabaseConfig (pydantic-settings), async SQLAlchemy engine + asyncpg |
| `environment/` | `common-environment` | EnvConfig (ENV_MODE, ENV_SERVICE_INTERNAL_HOST/PORT), EnvironmentEnum |
| `gateway/` | `common-gateway` | ServiceEnum (StrEnum), GatewayConfig (api_key), URL utils |
| `logger/` | `common-logger` | `get_logger()` — фабрика логгеров, подавление шумных библиотек |
| `redis/` | `common-redis` | Async/sync Redis клиенты, `@singleton` и `@cache` декораторы |
| `sentry/` | `common-sentry` | `init_sentry()` с CeleryIntegration |
| `shared/` | `common-shared` | BaseRepository, BaseUnitOfWork, middlewares, HTTP clients, serializers |

## Детали shared/

- `unitofwork.py` — `BaseUnitOfWork`: async context manager, rollback при исключении, защита от повторного входа
- `repositories/base.py` — `BaseRepository`: базовые CRUD операции для SQLAlchemy моделей
- `api/middlewares.py` — `LoggingMiddleware` для FastAPI
- `api/exceptions.py` — `http_exception_custom_handler`
- `clients/base.py` — `BaseClient`: httpx AsyncClient, автоматически проставляет `x-api-key`
- `clients/head_hunter/` — `HeadHunterClient`: клиент к HH API и HH UI (резюме)
- `decorators/concurency.py` — `@limit_requests(n)`: semaphore + rate limiter per event loop
- `serializers/` — абстрактный сериализатор + JSON и Pickle реализации
- `services/base.py` — `BaseService`
- `schemas/model/` — утилиты для работы с Pydantic model fields

## Ключевые паттерны

- Каждая библиотека — отдельный `pyproject.toml`, добавляется в `uv.lock` как workspace member
- `get_logger(__name__)` — использовать везде, не создавать `logging.getLogger` напрямую
- `env_config.debug` — `True` только при `ENV_MODE=development`
- `BaseClient` автоматически добавляет `x-api-key` — все межсервисные запросы идут через api-gateway

## Зависимости

- Используются всеми Python сервисами в `services/`
- `shared` зависит от `database`, `environment`, `gateway`, `logger`, `redis`
