from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator
from schemas import HabrDetailedVacancySchema


__all__ = [
    "HabrVacanciesQuery",
    "HabrVacancyDetailedResponse",
    "HabrVacancyListResponse",
]


class HabrVacanciesQuery(BaseModel):
    date_gte: datetime | None = Field(
        None,
        description="Datetime in UTC, format: YYYY-MM-DDTHH:MM:SSZ or +00:00",
    )

    @field_validator("date_gte", mode="after")
    @classmethod
    def must_be_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("Datetime must include timezone and be in UTC (e.g. 2025-09-28T15:30:00Z)")
        if v.utcoffset() != UTC.utcoffset(v):
            raise ValueError("Timezone must be UTC (use Z or +00:00)")
        return v.astimezone(UTC)


class HabrVacancyListResponse(BaseModel):
    vacancies: list[int]


class HabrVacancyDetailedResponse(BaseModel):
    vacancy: HabrDetailedVacancySchema
