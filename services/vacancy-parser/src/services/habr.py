from repositories.habr import HabrVacancyRepository
from schemas.vacancies import HabrVacancyCreate, HabrVacancyRead

from services import BaseVacancyService


class HabrVacancyService(BaseVacancyService[HabrVacancyRead, HabrVacancyCreate, HabrVacancyRepository]):
    """Сервис для бизнес-логики, связанной с вакансиями из Habr."""

    read_schema = HabrVacancyRead
    create_schema = HabrVacancyCreate
    repo: "HabrVacancyRepository"

    def _get_repo(self) -> "HabrVacancyRepository":
        return self._uow.habr_vacancies

    async def get_last_vacancy(self) -> HabrVacancyRead | None:
        vacancy = await self.repo.get_last_vacancy()

        return self.read_schema.model_validate(vacancy) if vacancy else None
