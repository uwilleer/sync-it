from repositories import HeadHunterVacancyRepository
from schemas.vacancies import HeadHunterVacancyCreate, HeadHunterVacancyRead

from services import BaseVacancyService


__all__ = ["HeadHunterVacancyService"]


class HeadHunterVacancyService(
    BaseVacancyService[HeadHunterVacancyRead, HeadHunterVacancyCreate, HeadHunterVacancyRepository]
):
    """Сервис для бизнес-логики, связанной с вакансиями из HeadHunter."""

    read_schema = HeadHunterVacancyRead
    create_schema = HeadHunterVacancyCreate
    repo: "HeadHunterVacancyRepository"

    def _get_repo(self) -> "HeadHunterVacancyRepository":
        return self._uow.hh_vacancies

    async def get_vacancy_by_id(self, vacancy_id: int) -> HeadHunterVacancyRead | None:
        vacancy = await self.repo.get_vacancy_by_id(vacancy_id)

        return self.read_schema.model_validate(vacancy) if vacancy else None
