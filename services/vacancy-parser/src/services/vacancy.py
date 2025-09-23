from repositories import VacancyRepository
from schemas.vacancies import VacancyRead

from services import BaseVacancyService


__all__ = ["VacancyService"]


class VacancyService(BaseVacancyService[VacancyRead, None, VacancyRepository]):
    _read_schema = VacancyRead
    _create_schema = None
    _repo: "VacancyRepository"

    def _get_repo(self) -> "VacancyRepository":
        return self._uow.vacancies
