from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

from common.logger import get_logger
from common.shared.repositories import BaseRepository
from database.models import Vacancy
from database.models.enums import SourceEnum
from schemas.vacancy import VacanciesSummarySchema
from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload, selectinload


__all__ = ["VacancyRepository"]


logger = get_logger(__name__)


TSelect = TypeVar("TSelect", bound=Select[Any])


class VacancyRepository(BaseRepository):
    """Репозиторий для управления вакансиями."""

    MIN_SIMILARITY_PERCENT = 60  # Минимальное соотношение совпадающих навыков
    MIN_SKILLS_COUNT = 5
    BONUS_MIN_SKILL = 7  # Бонус за каждый навык сверх MIN_SKILLS_COUNT
    PENALTY_MISSING_SKILL = 5  # Штраф за каждый отсутствующий навык
    BEST_SKILLS_COUNT_BONUS = 25
    DAYS_INTERVAL = timedelta(days=21)
    DAYS_RELEVANCE_BONUS = 10

    async def add(self, vacancy: Vacancy) -> Vacancy:
        """Добавляет экземпляр вакансии в сессию."""
        self._session.add(vacancy)
        await self._session.flush()
        await self._session.refresh(vacancy, attribute_names=["profession", "skills", "grades", "work_formats"])

        return vacancy

    async def get_existing_hashes(self, hashes: Iterable[str]) -> set[str]:
        """Получить set уже существующих хешей в БД."""
        stmt = select(Vacancy.hash).where(Vacancy.hash.in_(hashes))
        result = await self._session.execute(stmt)

        return set(result.scalars().all())

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        """Получает вакансию по ее id."""
        stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
        stmt = self._apply_vacancy_prefetch_details_to_stmt(stmt)
        result = await self._session.execute(stmt)

        return result.unique().scalar_one_or_none()

    async def get_summary(self) -> VacanciesSummarySchema:  # noqa: PLR0914
        """Возвращает агрегированную статистику по вакансиям."""

        now = datetime.now(UTC)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Общее количество
        total_stmt = select(func.count(Vacancy.id))
        total = (await self._session.execute(total_stmt)).scalar_one()

        # Количество по источникам
        sources_stmt = select(Vacancy.source, func.count(Vacancy.id)).group_by(Vacancy.source)
        sources_result = await self._session.execute(sources_stmt)
        raw_sources: dict[str, int] = dict(sources_result.tuples().all())
        # FIXME Костыльно
        sources: dict[str, int] = {source.value: raw_sources.get(source.value, 0) for source in SourceEnum}

        # За день
        day_stmt = select(func.count(Vacancy.id)).where(Vacancy.published_at >= day_ago)
        day_result = await self._session.execute(day_stmt)
        day_count = day_result.scalar_one()

        # За неделю
        week_stmt = select(func.count(Vacancy.id)).where(Vacancy.published_at >= week_ago)
        week_result = await self._session.execute(week_stmt)
        week_count = week_result.scalar_one()

        # За месяц
        month_stmt = select(func.count(Vacancy.id)).where(Vacancy.published_at >= month_ago)
        month_result = await self._session.execute(month_stmt)
        month_count = month_result.scalar_one()

        return VacanciesSummarySchema(
            total=total,
            sources=sources,
            day_count=day_count,
            week_count=week_count,
            month_count=month_count,
        )

    @staticmethod
    def _apply_vacancy_prefetch_details_to_stmt(stmt: TSelect) -> TSelect:
        return stmt.options(
            joinedload(Vacancy.profession),
            selectinload(Vacancy.grades),
            selectinload(Vacancy.work_formats),
            selectinload(Vacancy.skills),
        )
