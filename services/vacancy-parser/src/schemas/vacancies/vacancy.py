from datetime import datetime

from pydantic import ConfigDict
from schemas.vacancies import BaseVacancyRead


__all__ = ["VacancyRead"]


class VacancyRead(BaseVacancyRead):
    id: int
    hash: str
    data: str
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
