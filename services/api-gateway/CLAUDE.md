# api-gateway

FastAPI прокси-шлюз — единая точка входа для всех внешних запросов.

## Структура

- `src/main.py` — FastAPI app, маршруты GET/POST/DELETE `/{service}/{path:path}`
- `src/clients/proxy.py` — `_ProxyClient`: перенаправляет запросы на внутренние сервисы по `ServiceEnum`
- `src/dependencies.py` — `validate_api_key`: проверка `X-API-Key` header
- `src/schemas.py` — `HealthResponse`

## Ключевые паттерны

- URL строится как `http://{service_name}:{ENV_SERVICE_INTERNAL_PORT}/{path}` — имя сервиса = DNS в Docker сети
- `ServiceEnum` из `libs/common/gateway/enums.py` — исчерпывающий список допустимых сервисов
- В dev-режиме (`ENV_MODE=development`) проверка API ключа пропускается
- Telegram webhook (`/telegram-bot/webhook/*`) пропускается без ключа — нельзя передавать X-API-Key в Telegram

## Зависимости

- `libs/common/gateway` — `ServiceEnum`, `gateway_config` (содержит `api_key`)
- `libs/common/environment` — `env_config.debug`, `env_config.service_internal_port`
- `libs/common/shared/clients` — `BaseClient` (автоматически проставляет `x-api-key` заголовок)

## Конфигурация

```
GATEWAY_API_KEY=...        # API ключ для входящих запросов
GATEWAY_HOST=...           # хост для uvicorn
GATEWAY_PORT=...           # порт для uvicorn
ENV_MODE=...               # development/production
ENV_SERVICE_INTERNAL_PORT= # порт внутренних сервисов (одинаковый для всех)
```

## Миграции

Нет базы данных, миграции не нужны.
