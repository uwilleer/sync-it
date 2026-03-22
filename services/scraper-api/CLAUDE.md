# scraper-api

FastAPI сервис парсинга Telegram каналов и Habr Career через Telethon MTProto клиент.

## Структура

- `src/main.py` — FastAPI app, lifespan запускает/останавливает Telethon
- `src/api/v1/telegram/` — endpoint для получения сообщений из Telegram топиков
- `src/api/v1/habr/` — endpoint для получения вакансий с Habr Career
- `src/clients/telethon/client.py` — `TelethonClient`: обёртка над `TelegramClient`
- `src/clients/habr.py` — HTTP клиент к Habr API
- `src/parsers/telegram.py` — парсер сообщений Telegram
- `src/parsers/habr.py` — парсер вакансий Habr
- `src/core/config.py` — конфигурация (Telethon credentials)

## Ключевые паттерны

- Telethon сессия передаётся через `StringSession` (`SCRAPER_API_TELETHON_SESSION_STRING`), без файлов на диске
- Сессия инициализируется на уровне модуля при импорте `clients/telethon/client.py`
- `TelethonClient.start()` вызывается в lifespan FastAPI, `stop()` — при shutdown

## Зависимости

- Вызывается из: `vacancy-parser` (через api-gateway)
- Внешние API: Telegram MTProto, Habr Career API

## Конфигурация

```
SCRAPER_API_TELETHON_SESSION_STRING=...  # StringSession строка (scripts/generate_telethon_session.py)
SCRAPER_API_TELETHON_API_ID=...
SCRAPER_API_TELETHON_API_HASH=...
ENV_MODE=...
ENV_SERVICE_INTERNAL_HOST=...
ENV_SERVICE_INTERNAL_PORT=...
```

## Миграции

Нет базы данных.
