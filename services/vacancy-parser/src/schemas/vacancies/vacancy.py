from datetime import datetime
from typing import Any

from schemas.vacancies import BaseVacancyCreate, BaseVacancyRead


__all__ = [
    "VacancyCreate",
    "VacancyRead",
]


class VacancyRead(BaseVacancyRead):
    id: int
    hash: str
    data: str
    processed_at: datetime | None


class VacancyCreate(BaseVacancyCreate):
    def __init__(self, **kwargs: dict[Any, Any]) -> None:
        super().__init__(**kwargs)
        raise TypeError("Нельзя создавать экземпляры `VacancyCreate` напрямую.")
