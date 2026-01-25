from common.shared.schemas.http import HttpsUrl
from database.models.enums import SourceEnum
from pydantic import BaseModel, computed_field, field_serializer


class BaseVacancyRead(BaseModel):
    pass


class BaseVacancyCreate(BaseModel):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        raise NotImplementedError("Define hash in child class")

    @field_serializer("link", check_fields=False)
    def serialize_link(self, link: HttpsUrl) -> str:  # noqa: PLR6301
        return str(link)

    @field_serializer("source", check_fields=False)
    def serialize_source(self, source: SourceEnum) -> str:  # noqa: PLR6301
        return str(source)
