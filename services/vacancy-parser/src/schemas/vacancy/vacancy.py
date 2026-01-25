from datetime import datetime
from typing import Any

from common.shared.schemas.http import HttpsUrl
from common.shared.schemas.model import ModelFields
from database.models import Vacancy
from database.models.enums import SourceEnum
from pydantic import ConfigDict
from schemas.vacancy import BaseVacancyCreate, BaseVacancyRead


class VacancyFields(ModelFields):
    __model__ = Vacancy

    id: int
    source: SourceEnum
    hash: str
    fingerprint: str
    link: HttpsUrl
    data: str
    published_at: datetime
    processed_at: datetime | None


class VacancyRead(BaseVacancyRead):
    id: int = VacancyFields.id
    hash: str = VacancyFields.hash
    data: str = VacancyFields.data
    processed_at: datetime | None = VacancyFields.processed_at

    model_config = ConfigDict(from_attributes=True)


class VacancyCreate(BaseVacancyCreate):
    def __init__(self, **kwargs: dict[Any, Any]) -> None:
        super().__init__(**kwargs)
        raise TypeError("Нельзя создавать экземпляры `VacancyCreate` напрямую.")
