# vacancy-processor

FastAPI + Celery сервис анализа, структурирования и хранения обработанных вакансий.

## Структура

- `src/main.py` — FastAPI app
- `src/celery_app/beat.py` — расписание: `process_vacancies` каждые 5 минут
- `src/tasks/vacancies.py` — Celery task `process_vacancies`: поллинг вакансий из vacancy-parser и обработка
- `src/utils/processor.py` — `VacancyProcessor`: оркестратор обработки (получить → prompt → LLM → extract → save)
- `src/utils/extractor.py` — `VacancyExtractor`: парсит LLM completion в структурированные поля
- `src/utils/prompter.py` — `make_vacancy_prompt()`: формирует prompt из сырого текста вакансии
- `src/clients/gpt.py` — клиент к gpt-api
- `src/clients/vacancy.py` — клиент к vacancy-parser (забрать сырые вакансии, пометить как processed)
- `src/api/v1/` — endpoints: vacancies, grades, professions, skills, work_formats
- `src/database/models/` — `Vacancy`, `Grade`, `Profession`, `Skill`, `WorkFormat`, M2M таблицы
- `src/seeds/` — начальные данные для справочников (grades, professions, skills, work_formats)
- `src/services/` — бизнес-логика по каждой сущности
- `src/unitofwork.py` — `UnitOfWork`
- `src/core/config.py` — `VACANCY_PROCESSOR_DB_SCHEMA=vacancy_processor`

## Ключевые паттерны

- `@singleton(timedelta(minutes=60))` — Redis lock на задачу `process_vacancies`
- Обработка идёт пачками: `processor.start()` возвращает количество обработанных; цикл до 0
- LLM completion проверяется на "Не вакансия" — отфильтровывает нерелевантные объявления
- Дубликаты (IntegrityError на unique hash) — логируются и пропускаются
- Три Docker контейнера: `vacancy-processor`, `vacancy-processor-worker`, `vacancy-processor-beat`
- Данный сервис является **источником данных для vacancy-matcher** (Go сервис читает схему `vacancy_processor` напрямую)

## БД схема (`vacancy_processor` в PostgreSQL)

- `vacancies` — обработанные вакансии (source, hash, link, company_name, salary, responsibilities, requirements, conditions, published_at, profession_id)
- `professions`, `grades`, `skills`, `work_formats` — справочники
- `vacancy_grades`, `vacancy_skills`, `vacancy_work_formats` — M2M связи

## Миграции

```bash
make mm s=vacancy-processor m="message"
make migrate s=vacancy-processor
```

## Зависимости

- Вызывает: vacancy-parser (получение необработанных), gpt-api (LLM analysis)
- Вызывается из: telegram-bot (справочники grades/professions/skills/work_formats), vacancy-matcher (прямой SELECT)
- Redis — брокер Celery
- pgbouncer — PostgreSQL

## Конфигурация

```
VACANCY_PROCESSOR_DB_SCHEMA=vacancy_processor
ENV_MODE=...
ENV_SERVICE_INTERNAL_HOST=...
ENV_SERVICE_INTERNAL_PORT=...
DATABASE_HOST/PORT/DB/USER/PASSWORD=...
REDIS_DSN=...
```
