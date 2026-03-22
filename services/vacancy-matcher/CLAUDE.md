# vacancy-matcher

Go (net/http + GORM) сервис матчинга вакансий по навыкам пользователя.

## Структура

```
cmd/matcher/main.go          — точка входа, wire-up зависимостей, HTTP server
internal/
  domain/                    — доменные типы: Vacancy, Grade, Profession, Skill, WorkFormat
  dto/vacancy.go             — RelevantVacancyFilter, VacancyWithNeighbors, scoring-константы
  handlers/vacancy.go        — GET /api/v1/vacancies/match (POST запрос с JSON body)
  handlers/health.go         — GET /health
  repositories/vacancy.go    — raw SQL запрос с scoring-логикой
  services/vacancy.go        — навигация prev/next вакансии в отсортированном списке
pkg/db/db.go                 — инициализация GORM подключения к PostgreSQL
.air.toml                    — конфигурация Air (hot reload в dev)
```

## Алгоритм матчинга

1. SQL: подсчёт `common_skills_count` и `total_skills_count` для каждой вакансии из схемы `vacancy_processor`
2. Фильтр: `base_similarity >= MinSimilarityPercent (60%)`
3. Go: вычисление score = `base_similarity + bonusMinSkills + subsetBonus + relevanceBonus - missingSkillsPenalty`
4. Сортировка по score DESC, top 50 вакансий
5. Возврат текущей вакансии + prev_id/next_id для навигации

Константы (в `dto/vacancy.go`): `MinSimilarityPercent=60`, `DaysInterval=3`, `BonusMinSkill=7`, `PenaltyMissingSkill=5`, `BestSkillsCountBonus=15`, `DaysRelevanceBonus=15`

## Ключевые паттерны

- Читает схему `vacancy_processor` напрямую (не через API) — нет своей БД
- `net/http` стандартная библиотека без фреймворков
- GORM используется только для `Preload` relations после raw SQL фильтрации
- Не входит в uv workspace — отдельный Go модуль

## Зависимости

- Читает: `vacancy_processor.vacancies`, `vacancy_processor.skills`, `vacancy_processor.grades`, `vacancy_processor.work_formats`, `vacancy_processor.professions`
- Вызывается из: telegram-bot (через api-gateway)
- Зависит от: vacancy-processor (должен быть healthy в docker-compose)

## Конфигурация

```
ENV_SERVICE_INTERNAL_PORT=...
DATABASE_HOST/PORT/DB/USER/PASSWORD=...  # прямое подключение, без pgbouncer
```

## Разработка

```bash
# В dev-режиме (Air hot reload)
air  # запускается автоматически Docker entrypoint

# Сборка вручную
go build ./cmd/matcher/...
```
