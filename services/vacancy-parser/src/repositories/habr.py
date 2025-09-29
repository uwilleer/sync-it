from datetime import datetime

from database.models import HabrVacancy
from repositories import BaseVacancyRepository
from sqlalchemy import func, select


__all__ = ["HabrVacancyRepository"]


class HabrVacancyRepository(BaseVacancyRepository[HabrVacancy]):
    model = HabrVacancy

    async def get_last_published_at(self) -> datetime | None:
        """Возвращает дату последней вакансии."""
        stmt = select(func.max(self.model.published_at))
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()
