from pydantic import BaseModel, Field
from schemas.vacancies.vacancy import VacancyRead


__all__ = [
    "VacancyListResponse",
    "VacancyProcessedResponse",
]


class VacancySchema(VacancyRead):
    fingerprint: str = Field(exclude=True)


class VacancyListResponse(BaseModel):
    vacancies: list[VacancySchema]


class VacancyProcessedResponse(BaseModel):
    is_processed: bool
