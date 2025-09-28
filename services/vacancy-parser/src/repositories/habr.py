from database.models import HabrVacancy
from repositories import BaseVacancyRepository


__all__ = ["HabrVacancyRepository"]


class HabrVacancyRepository(BaseVacancyRepository[HabrVacancy]):
    model = HabrVacancy
