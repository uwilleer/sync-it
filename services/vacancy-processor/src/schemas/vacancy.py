from datetime import datetime
from typing import Any

from common.shared.schemas.http import HttpsUrl
from common.shared.schemas.model import ModelFields
from database.models import Vacancy
from database.models.enums import SourceEnum
from pydantic import BaseModel, ConfigDict, field_serializer
from schemas.grade import GradeRead
from schemas.profession import ProfessionRead
from schemas.skill import SkillRead
from schemas.work_format import WorkFormatRead


class VacancyFields(ModelFields):
    __model__ = Vacancy

    id: int
    source: SourceEnum
    hash: str
    link: HttpsUrl
    company_name: str | None
    salary: str | None
    workplace_description: str | None
    responsibilities: str | None
    requirements: str | None
    conditions: str | None
    published_at: datetime
    profession_id: int | None
    profession: Any | None
    grades: list[Any] | None
    work_formats: list[Any] | None
    skills: list[Any] | None


class VacancyCreate(BaseModel):
    source: SourceEnum = VacancyFields.source
    hash: str = VacancyFields.hash
    link: HttpsUrl = VacancyFields.link

    profession_id: int | None = VacancyFields.profession_id

    company_name: str | None = VacancyFields.company_name
    salary: str | None = VacancyFields.salary
    workplace_description: str | None = VacancyFields.workplace_description
    responsibilities: str | None = VacancyFields.responsibilities
    requirements: str | None = VacancyFields.requirements
    conditions: str | None = VacancyFields.conditions
    published_at: datetime = VacancyFields.published_at

    @field_serializer("link")
    def serialize_url(self, link: HttpsUrl) -> str:  # noqa: PLR6301
        return str(link)


class VacancyRead(BaseModel):
    id: int = VacancyFields.id

    source: SourceEnum = VacancyFields.source
    hash: str = VacancyFields.hash
    link: HttpsUrl = VacancyFields.link

    company_name: str | None = VacancyFields.company_name
    salary: str | None = VacancyFields.salary
    workplace_description: str | None = VacancyFields.workplace_description
    responsibilities: str | None = VacancyFields.responsibilities
    requirements: str | None = VacancyFields.requirements
    conditions: str | None = VacancyFields.conditions

    published_at: datetime = VacancyFields.published_at

    profession: ProfessionRead | None = VacancyFields.profession
    skills: list[SkillRead] | None = VacancyFields.skills
    grades: list[GradeRead] | None = VacancyFields.grades
    work_formats: list[WorkFormatRead] | None = VacancyFields.work_formats

    model_config = ConfigDict(from_attributes=True)


class VacanciesSummarySchema(BaseModel):
    total: int
    sources: dict[SourceEnum, int]
    day_count: int
    week_count: int
    month_count: int
