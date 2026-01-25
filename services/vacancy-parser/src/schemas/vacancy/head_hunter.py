from datetime import datetime

from common.shared.schemas.http import HttpsUrl
from database.models import HeadHunterVacancy
from database.models.enums import SourceEnum
from pydantic import ConfigDict, Field, computed_field
from schemas.vacancy import BaseVacancyCreate, BaseVacancyRead
from schemas.vacancy.vacancy import VacancyFields
from utils import generate_vacancy_hash


class HeadHunterVacancyFields(VacancyFields):
    __model__ = HeadHunterVacancy

    vacancy_id: int


class HeadHunterVacancyCreate(BaseVacancyCreate):
    fingerprint: str = HeadHunterVacancyFields.fingerprint
    link: HttpsUrl = HeadHunterVacancyFields.link
    published_at: datetime = HeadHunterVacancyFields.published_at
    vacancy_id: int = HeadHunterVacancyFields.vacancy_id

    employer: str = Field(exclude=True)
    name: str = Field(exclude=True)
    description: str = Field(exclude=True)
    salary: str | None = Field(exclude=True)
    experience: str = Field(exclude=True)
    schedule: str = Field(exclude=True)
    work_formats: list[str] = Field(exclude=True)
    key_skills: list[str] = Field(exclude=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return generate_vacancy_hash(self.vacancy_id, SourceEnum.HEAD_HUNTER)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def source(self) -> SourceEnum:
        return SourceEnum.HEAD_HUNTER

    @computed_field  # type: ignore[prop-decorator]
    @property
    def data(self) -> str:
        text_parts: list[str] = [f"Компания: {self.employer}", f"Вакансия: {self.name}"]
        if self.salary:
            text_parts.append(f"Зарплата: {self.salary}")
        text_parts.extend(
            (
                f"Опыт: {self.experience}",
                f"График работы: {self.schedule}",
            )
        )
        if self.work_formats:
            text_parts.append(f"Формат работы: {' '.join(self.work_formats)}")
        if self.key_skills:
            text_parts.append(f"Ключевые навыки: {' '.join(self.key_skills)}")
        text_parts.append(f"Описание: \n{self.description}")

        return "\n".join(text_parts)


class HeadHunterVacancyRead(BaseVacancyRead):
    id: int = HeadHunterVacancyFields.id
    hash: str = HeadHunterVacancyFields.hash
    data: str = HeadHunterVacancyFields.data
    source: SourceEnum = HeadHunterVacancyFields.source
    fingerprint: str = HeadHunterVacancyFields.fingerprint
    link: HttpsUrl = HeadHunterVacancyFields.link
    published_at: datetime = HeadHunterVacancyFields.published_at
    vacancy_id: int = HeadHunterVacancyFields.vacancy_id

    model_config = ConfigDict(from_attributes=True)
