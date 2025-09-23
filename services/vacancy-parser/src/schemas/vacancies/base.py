from datetime import datetime

from common.shared.schemas import HttpsUrl
from database.models.enums import SourceEnum
from pydantic import BaseModel, computed_field


__all__ = [
    "BaseVacancy",
    "BaseVacancyCreate",
    "BaseVacancyRead",
]


class BaseVacancy(BaseModel):
    source: SourceEnum
    fingerprint: str
    link: HttpsUrl
    published_at: datetime


class BaseVacancyCreate(BaseVacancy):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        raise NotImplementedError("Define hash in child class")


class BaseVacancyRead(BaseVacancy):
    hash: str
