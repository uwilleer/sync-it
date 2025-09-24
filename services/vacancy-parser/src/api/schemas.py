from pydantic import BaseModel, Field


__all__ = [
    "HealthResponse",
    "VacanciesListQuery",
]


class HealthResponse(BaseModel):
    status: str


class VacanciesListQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Лимит вакансий")
