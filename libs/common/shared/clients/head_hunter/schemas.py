from datetime import datetime

from common.logger import get_logger
from common.shared.clients.head_hunter.enums import SalaryCurrency, SalaryMode
from pydantic import BaseModel, Field, field_validator


__all__ = [
    "HeadHunterVacancyDetailResponse",
    "HeadHunterVacancyListResponse",
    "HeadHunterVacancySchema",
]


logger = get_logger(__name__)


class HeadHunterVacancySalaryModeSchema(BaseModel):
    id: SalaryMode | None

    @field_validator("id", mode="before")
    @classmethod
    def _validate_id(cls, mode: SalaryMode | None) -> SalaryMode | None:
        if mode is None:
            return None

        if mode != SalaryMode.MONTH:
            logger.warning("Salary mode '%s' is not supported.", mode)
            return None

        return mode

    def humanize(self) -> str | None:
        return self.id.humanize() if self.id else None


class HeadHunterVacancySalarySchema(BaseModel):
    from_: int | None = None
    to: int | None = None
    currency: SalaryCurrency
    mode: HeadHunterVacancySalaryModeSchema

    def humanize(self) -> str | None:
        """Преобразует данные о зарплате в человеко-читаемое представление."""
        if not self.from_ and not self.to:
            return None

        if self.from_ and not self.to:
            return f"от {self.from_} {self.currency.humanize()} {self.mode.humanize()}"

        if not self.from_ and self.to:
            return f"до {self.to} {self.currency.humanize()} {self.mode.humanize()}"

        return f"от {self.from_} до {self.to} {self.currency.humanize()} {self.mode.humanize()}"


class HeadHunterVacancySchema(BaseModel):
    id: int


class HeadHunterVacancyExperienceSchema(BaseModel):
    id: str
    name: str


class HeadHunterVacancyScheduleSchema(BaseModel):
    id: str
    name: str


class HeadHunterVacancyWorkFormatSchema(BaseModel):
    id: str
    name: str


class HeadHunterVacancyKeySkillSchema(BaseModel):
    name: str


class HeadHunterVacancyEmployerSchema(BaseModel):
    name: str


class HeadHunterVacancyDetailResponse(HeadHunterVacancySchema):
    id: int
    alternate_url: str  # Ссылка на вакансию UI версию HH
    employer: HeadHunterVacancyEmployerSchema
    name: str
    description: str
    salary: HeadHunterVacancySalarySchema | None = Field(alias="salary_range")  # salary - deprecated.
    experience: HeadHunterVacancyExperienceSchema
    schedule: HeadHunterVacancyScheduleSchema
    work_format: list[HeadHunterVacancyWorkFormatSchema]
    key_skills: list[HeadHunterVacancyKeySkillSchema]
    published_at: datetime


class HeadHunterVacancyListResponse(BaseModel):
    items: list[HeadHunterVacancySchema]
    page: int
    pages: int
    per_page: int
    found: int
