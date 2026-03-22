# gpt-api

FastAPI сервис для получения LLM completions через официальный OpenAI API (модель gpt-5-nano).

## Структура

- `src/main.py` — FastAPI app, подключает `api/v1` router
- `src/api/v1/completion.py` — endpoint `POST /api/v1/completion`
- `src/services/gpt.py` — `get_gpt_response(prompt)`: вызов OpenAI API с retry (3 попытки, задержка 3с)
- `src/core/config.py` — конфигурация сервиса (API key, proxy, model)
- `src/schemas.py` — request/response схемы
- `src/utils.py` — вспомогательные утилиты

## Ключевые паттерны

- Клиент: `openai.AsyncOpenAI` с поддержкой HTTP-прокси через `httpx.AsyncClient`
- `@limit_requests(64)` — ограничение параллельных запросов к LLM
- При ошибке возвращает `None`, caller (vacancy-processor) обрабатывает как "не вакансия"
- `MAX_RETRIES = 3`, `RETRY_DELAY = 3` секунды

## Зависимости

- Вызывается из: `vacancy-processor` (через api-gateway)
- `libs/common/shared/decorators/concurency` — `@limit_requests`
- PyPI: `openai`, `httpx`

## Конфигурация

```
ENV_MODE=...
ENV_SERVICE_INTERNAL_HOST=...
ENV_SERVICE_INTERNAL_PORT=...
GPT_API_OPENAI_API_KEY=sk-...          # обязательный
GPT_API_OPENAI_PROXY=http://host:port  # опциональный, HTTP прокси
GPT_API_OPENAI_MODEL=gpt-5-nano       # опциональный, по умолчанию gpt-5-nano
```

## Миграции

Нет базы данных.