from database.models import HeadHunterVacancy
from repositories import BaseVacancyRepository
from sqlalchemy import select


__all__ = ["HeadHunterVacancyRepository"]


class HeadHunterVacancyRepository(BaseVacancyRepository[HeadHunterVacancy]):
    _model = HeadHunterVacancy

    async def get_vacancy_by_id(self, vacancy_id: int) -> HeadHunterVacancy | None:
        stmt = select(self._model).where(self._model.vacancy_id == vacancy_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()
