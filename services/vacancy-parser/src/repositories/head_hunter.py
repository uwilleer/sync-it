from database.models import HeadHunterVacancy
from repositories import BaseVacancyRepository


__all__ = ["HeadHunterVacancyRepository"]


class HeadHunterVacancyRepository(BaseVacancyRepository[HeadHunterVacancy]):
    model = HeadHunterVacancy
