from pydantic import BaseModel, ConfigDict, Field
from schemas.vacancies.vacancy import VacancyRead


__all__ = [
    "VacanciesListQuery",
    "VacancyListResponse",
    "VacancyProcessedBody",
    "VacancyProcessedResponse",
]


class VacancySchema(VacancyRead):
    fingerprint: str = Field(exclude=True)


class VacanciesListQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Лимит вакансий")

    model_config = ConfigDict(extra="forbid")


class VacancyListResponse(BaseModel):
    vacancies: list[VacancySchema]


class VacancyProcessedBody(BaseModel):
    hashes: list[str] = Field(description="Хеши вакансий")

    model_config = ConfigDict(extra="forbid")


class VacancyProcessedResponse(BaseModel):
    count: int
