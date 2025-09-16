from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, timedelta
import operator
from typing import Any, TypeVar

from common.logger import get_logger
from common.shared.repositories import BaseRepository
from database.models import Grade, Profession, Vacancy, WorkFormat
from database.models.enums import GradeEnum, ProfessionEnum, SkillEnum, WorkFormatEnum
from schemas.vacancy import VacanciesSummarySchema
from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload, selectinload


__all__ = ["VacancyRepository"]


logger = get_logger(__name__)


TSelect = TypeVar("TSelect", bound=Select[Any])


class VacancyRepository(BaseRepository):
    """Репозиторий для управления вакансиями."""

    MIN_SIMILARITY_PERCENT = 25  # Минимальное соотношение совпадающих навыков
    MIN_SKILLS_COUNT = 5
    BONUS_MIN_SKILL = 5  # Бонус за каждый навык сверх MIN_SKILLS_COUNT
    BEST_SKILLS_COUNT_BONUS = 10
    DAYS_INTERVAL = timedelta(days=30)
    DAYS_RELEVANCE_BONUS = 4

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

    async def get_all(self, limit: int) -> Sequence[Vacancy]:
        """Получает отфильтрованный список вакансий."""
        stmt = select(Vacancy)
        stmt = self._apply_vacancy_prefetch_details_to_stmt(stmt)
        stmt = stmt.order_by(Vacancy.published_at.desc()).limit(limit)

        result = await self._session.execute(stmt)

        return result.scalars().unique().all()

    async def get_relevant(
        self,
        professions: Sequence[ProfessionEnum],
        grades: Sequence[GradeEnum],
        work_formats: Sequence[WorkFormatEnum],
        skills: Sequence[SkillEnum],
    ) -> list[Vacancy]:
        """
        Находит вакансию по ID и ее соседей в списке, отсортированном по релевантности,
        выполняя все вычисления на стороне БД.
        """
        stmt = (
            select(Vacancy).where(Vacancy.published_at >= (datetime.now(UTC) - self.DAYS_INTERVAL)).order_by(Vacancy.id)
        )
        stmt = self._apply_vacancy_prefetch_details_to_stmt(stmt)

        if professions:
            stmt = stmt.join(Profession).filter(Profession.name.in_(professions))
        if grades:
            stmt = stmt.join(Vacancy.grades).filter(Grade.name.in_(grades))
        if work_formats:
            stmt = stmt.join(Vacancy.work_formats).filter(WorkFormat.name.in_(work_formats))

        result = await self._session.execute(stmt)
        vacancies = result.scalars().unique().all()

        scored_vacancies: list[tuple[float, Vacancy]] = []
        user_skills_set = set(skills)

        for vacancy in vacancies:
            vacancy_skills_set = {skill.name for skill in vacancy.skills}

            common_skills = user_skills_set & vacancy_skills_set
            if not common_skills:
                continue

            common_count = len(common_skills)

            similarity = (common_count / len(vacancy_skills_set)) * 100
            if similarity < self.MIN_SIMILARITY_PERCENT:
                continue

            # Бонус за превышение минимального количества навыков
            if common_count > self.MIN_SKILLS_COUNT:
                bonus = (common_count - self.MIN_SKILLS_COUNT) * self.BONUS_MIN_SKILL
                similarity += bonus

            # Бонус за идеальное совпадение (все навыки пользователя есть в вакансии)
            if user_skills_set.issubset(vacancy_skills_set):
                similarity += 10

            # Бонус за актуальность вакансии
            days_since_published = (datetime.now(UTC) - vacancy.published_at).days
            relevance_bonus = max(0, 7 - days_since_published) * self.DAYS_RELEVANCE_BONUS
            similarity += relevance_bonus

            if similarity >= self.MIN_SIMILARITY_PERCENT:
                scored_vacancies.append((similarity, vacancy))

        return [v for _, v in sorted(scored_vacancies, key=operator.itemgetter(0), reverse=True)]

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
        sources: dict[str, int] = dict(sources_result.tuples().all())

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
