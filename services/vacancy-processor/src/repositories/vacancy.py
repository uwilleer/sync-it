from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

from common.logger import get_logger
from common.shared.repositories import BaseRepository
from database.models import Grade, Profession, Skill, Vacancy, WorkFormat
from database.models.enums import GradeEnum, ProfessionEnum, SkillEnum, SourceEnum, WorkFormatEnum
from database.models.tables import (
    vacancy_grades_table,
    vacancy_skills_table,
    vacancy_work_formats_table,
)
from schemas.vacancy import VacanciesSummarySchema
from sqlalchemy import Select, case, exists, func, literal, select
from sqlalchemy.orm import joinedload, selectinload


__all__ = ["VacancyRepository"]


logger = get_logger(__name__)


TSelect = TypeVar("TSelect", bound=Select[Any])


class VacancyRepository(BaseRepository):
    """Репозиторий для управления вакансиями."""

    MIN_SIMILARITY_PERCENT = 60  # Минимальное соотношение совпадающих навыков
    MIN_SKILLS_COUNT = 3
    BONUS_MIN_SKILL = 3  # Бонус за каждый навык сверх MIN_SKILLS_COUNT
    BEST_SKILLS_COUNT_BONUS = 15
    DAYS_INTERVAL = timedelta(days=21)
    DAYS_RELEVANCE_BONUS = 5

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

    async def get_filtered(self, limit: int) -> Sequence[Vacancy]:
        """Получает отфильтрованный список вакансий."""
        stmt = select(Vacancy)
        stmt = self._apply_vacancy_prefetch_details_to_stmt(stmt)
        stmt = stmt.order_by(Vacancy.published_at.desc()).limit(limit)

        result = await self._session.execute(stmt)

        return result.scalars().unique().all()

    async def get_relevant(  # noqa: PLR0914
        self,
        professions: Sequence[ProfessionEnum],
        grades: Sequence[GradeEnum],
        work_formats: Sequence[WorkFormatEnum],
        skills: Sequence[SkillEnum],
        sources: Sequence[SourceEnum],
    ) -> Sequence[Vacancy]:
        """
        Находит вакансию по ID и ее соседей в списке, отсортированном по релевантности,
        выполняя все вычисления на стороне БД.
        """
        # Если навык не передан, результат пуст как и в прежней логике
        if not skills:
            return []

        since_dt = datetime.now(UTC) - self.DAYS_INTERVAL

        # Коррелированные подзапросы для подсчета количества навыков у вакансии и количества совпадающих
        vs = vacancy_skills_table.alias("vs")

        total_skills_count = (
            select(func.count())
            .select_from(vs.join(Skill, vs.c.skill_id == Skill.id))
            .where(vs.c.vacancy_id == Vacancy.id)
            .correlate(Vacancy)
            .scalar_subquery()
        )

        common_skills_count = (
            select(func.count())
            .select_from(vs.join(Skill, vs.c.skill_id == Skill.id))
            .where(vs.c.vacancy_id == Vacancy.id, Skill.name.in_(skills))
            .correlate(Vacancy)
            .scalar_subquery()
        )

        user_skills_count = literal(len(skills))

        # Базовое сходство без бонусов
        base_similarity = (common_skills_count * literal(100.0)) / func.nullif(total_skills_count, 0)

        # Бонус за превышение минимального количества навыков
        bonus_min_skills = func.greatest(common_skills_count - literal(self.MIN_SKILLS_COUNT), 0) * literal(
            self.BONUS_MIN_SKILL
        )

        # Бонус за идеальное совпадение (все навыки пользователя есть в вакансии)
        subset_bonus = case((common_skills_count == user_skills_count, literal(20)), else_=literal(0))

        # Бонус за актуальность вакансии
        days_since_published = func.floor(func.extract("epoch", func.now() - Vacancy.published_at) / literal(86400.0))
        relevance_bonus = func.greatest(literal(0), literal(7) - days_since_published) * literal(
            self.DAYS_RELEVANCE_BONUS
        )

        total_score = base_similarity + bonus_min_skills + subset_bonus + relevance_bonus

        filters = [
            Vacancy.published_at >= since_dt,
            total_skills_count > 0,
            common_skills_count > 0,
            base_similarity >= literal(self.MIN_SIMILARITY_PERCENT),
        ]

        # Источник
        if sources:
            filters.append(Vacancy.source.in_(sources))

        # Профессии (один-к-одному) — фильтруем по связанному объекту без множителя строк
        if professions:
            filters.append(Vacancy.profession.has(Profession.name.in_(professions)))

        # Грейды — EXISTS, чтобы избежать дублирования строк
        if grades:
            vg = vacancy_grades_table.alias("vg")
            filters.append(
                exists(
                    select(1)
                    .select_from(vg.join(Grade, vg.c.grade_id == Grade.id))
                    .where(vg.c.vacancy_id == Vacancy.id, Grade.name.in_(grades))
                )
            )

        # Форматы работы — EXISTS
        if work_formats:
            vwf = vacancy_work_formats_table.alias("vwf")
            filters.append(
                exists(
                    select(1)
                    .select_from(vwf.join(WorkFormat, vwf.c.work_format_id == WorkFormat.id))
                    .where(vwf.c.vacancy_id == Vacancy.id, WorkFormat.name.in_(work_formats))
                )
            )

        stmt = select(Vacancy, total_score.label("score")).where(*filters).order_by(total_score.desc()).limit(50)
        stmt = self._apply_vacancy_prefetch_details_to_stmt(stmt)

        result = await self._session.execute(stmt)
        return result.scalars().all()

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
