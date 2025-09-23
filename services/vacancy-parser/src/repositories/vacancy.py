from database.models import Vacancy
from repositories import BaseVacancyRepository


__all__ = ["VacancyRepository"]


class VacancyRepository(BaseVacancyRepository[Vacancy]):
    """Репозиторий для работы с моделями вакансий."""

    _model = Vacancy
