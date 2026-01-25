from repositories import VacancyRepository
from schemas.vacancy import VacancyRead
from schemas.vacancy.vacancy import VacancyCreate

from services import BaseVacancyService


__all__ = ["VacancyService"]


class VacancyService(BaseVacancyService[VacancyRead, VacancyCreate, VacancyRepository]):
    read_schema = VacancyRead
    create_schema = VacancyCreate
    repo: "VacancyRepository"

    def _get_repo(self) -> "VacancyRepository":
        return self._uow.vacancies
