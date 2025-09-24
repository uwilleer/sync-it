from datetime import datetime

from common.shared.schemas import HttpsUrl
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
    model_config = ConfigDict(json_encoders={HttpsUrl: str})

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        raise NotImplementedError("Define hash in child class")

    @field_serializer("link")
    def serialize_url(self, link: HttpsUrl) -> str:  # noqa: PLR6301
        return str(link)


class BaseVacancyRead(BaseVacancy):
    hash: str
