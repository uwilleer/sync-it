from datetime import datetime

from pydantic import BaseModel, Field


__all__ = [
    "HabrVacanciesDetailedResponse",
    "HabrVacanciesListResponse",
    "HabrVacanciesRequest",
    "HabrVacancySchema",
]


class HabrVacancyMetaSchema(BaseModel):
    total_pages: int = Field(alias="totalPages")


class HabrVacanciesRequest(BaseModel):
    date_gte: datetime | None


class HabrVacancySchema(BaseModel):
    id: int
    datetime: datetime
    text: str


class HabrVacanciesListResponse(BaseModel):
    vacancies: list[int]


class HabrVacanciesDetailedResponse(BaseModel):
    vacancy: HabrVacancySchema
