from datetime import datetime

from common.shared.schemas.http import HttpsUrl
from database.models.enums import SourceEnum
from pydantic import BaseModel, ConfigDict, computed_field, field_serializer


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

    @field_serializer("link")
    def serialize_link(self, link: HttpsUrl) -> str:  # noqa: PLR6301
        return str(link)

    @field_serializer("source")
    def serialize_source(self, source: SourceEnum) -> str:  # noqa: PLR6301
        return str(source)


class BaseVacancyRead(BaseVacancy):
    id: int
    hash: str

    model_config = ConfigDict(from_attributes=True)
