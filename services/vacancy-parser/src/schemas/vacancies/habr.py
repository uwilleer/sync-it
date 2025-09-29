from database.models.enums import SourceEnum
from pydantic import computed_field
from schemas.vacancies import BaseVacancy, BaseVacancyCreate, BaseVacancyRead
from utils import generate_vacancy_hash


__all__ = [
    "HabrVacancyCreate",
    "HabrVacancyRead",
]


class BaseHabrVacancy(BaseVacancy):
    source: SourceEnum = SourceEnum.HABR
    external_id: int


class HabrVacancyCreate(BaseHabrVacancy, BaseVacancyCreate):
    data: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return generate_vacancy_hash(self.external_id, SourceEnum.HABR)


class HabrVacancyRead(BaseHabrVacancy, BaseVacancyRead):
    pass
