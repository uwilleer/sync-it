from datetime import datetime

from common.shared.schemas import HttpsUrl
from database.models.enums import SourceEnum
from pydantic import BaseModel, Field


__all__ = [
    "CompletionResponse",
    "VacanciesListRequest",
    "VacancyListResponse",
    "VacancyProcessedResponse",
    "VacancySchema",
]


class CompletionResponse(BaseModel):
    message: str


class VacancySchema(BaseModel):
    id: int
    source: SourceEnum
    hash: str
    link: HttpsUrl
    data: str
    published_at: datetime


# FIXME: Дубляж. См. VacanciesListQuery
class VacanciesListRequest(BaseModel):
    limit: int = Field(ge=1, le=1000)


class VacancyListResponse(BaseModel):
    vacancies: list[VacancySchema]


# FIXME Дубляж
class VacancyProcessedBody(BaseModel):
    hashes: list[str]


class VacancyProcessedResponse(BaseModel):
    updated_count: int
