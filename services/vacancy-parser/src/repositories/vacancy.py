from collections.abc import Sequence

from database.models import HabrVacancy, HeadHunterVacancy, TelegramVacancy, Vacancy
from repositories import BaseVacancyRepository
from sqlalchemy import delete, func, select


__all__ = ["VacancyRepository"]


class VacancyRepository(BaseVacancyRepository[Vacancy]):
    """Репозиторий для работы с моделями вакансий."""

    model = Vacancy

    async def _get_duplicate_ids_by_fingerprint(self, limit: int | None = None) -> list[int]:
        """Возвращает ID вакансий-дублей по точному совпадению fingerprint.

        В каждой группе по одному fingerprint сохраняется запись с максимальным
        published_at (при равенстве — с максимальным id), остальные считаются дублями.
        """
        row_number = func.row_number().over(
            partition_by=self.model.fingerprint,
            order_by=(self.model.published_at.desc(), self.model.id.desc()),
        ).label("rn")

        subq = select(self.model.id, row_number).subquery()

        stmt = select(subq.c.id).where(subq.c.rn > 1)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _delete_by_ids(self, ids: Sequence[int]) -> int:
        """Удаляет вакансии и соответствующие записи из дочерних таблиц."""
        if not ids:
            return 0

        await self._session.execute(delete(HabrVacancy).where(HabrVacancy.id.in_(ids)))
        await self._session.execute(delete(HeadHunterVacancy).where(HeadHunterVacancy.id.in_(ids)))
        await self._session.execute(delete(TelegramVacancy).where(TelegramVacancy.id.in_(ids)))

        result = await self._session.execute(
            delete(Vacancy).where(Vacancy.id.in_(ids)).returning(Vacancy.id)
        )
        deleted_ids = result.scalars().all()
        return len(deleted_ids)

    async def cleanup_duplicates_by_fingerprint(self, limit: int | None = None) -> int:
        """Удаляет дубли вакансий по fingerprint, оставляя самую актуальную.

        Возвращает количество удалённых записей.
        """
        duplicate_ids = await self._get_duplicate_ids_by_fingerprint(limit=limit)
        return await self._delete_by_ids(duplicate_ids)
