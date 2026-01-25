from datetime import datetime

from repositories.habr import HabrVacancyRepository
from schemas.vacancy import HabrVacancyCreate, HabrVacancyRead

from services import BaseVacancyService


class HabrVacancyService(BaseVacancyService[HabrVacancyRead, HabrVacancyCreate, HabrVacancyRepository]):
    """Сервис для бизнес-логики, связанной с вакансиями из Habr."""

    read_schema = HabrVacancyRead
    create_schema = HabrVacancyCreate
    repo: "HabrVacancyRepository"

    def _get_repo(self) -> "HabrVacancyRepository":
        return self._uow.habr_vacancies

    async def get_last_vacancy_published_at(self) -> datetime | None:
        return await self.repo.get_last_published_at()
