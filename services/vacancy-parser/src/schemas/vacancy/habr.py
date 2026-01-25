from datetime import datetime

from common.shared.schemas.http import HttpsUrl
from database.models import HabrVacancy
from database.models.enums import SourceEnum
from pydantic import ConfigDict, computed_field
from schemas.vacancy import BaseVacancyCreate, BaseVacancyRead, VacancyFields
from utils import generate_vacancy_hash


class HabrVacancyFields(VacancyFields):
    __model__ = HabrVacancy

    external_id: int


class HabrVacancyCreate(BaseVacancyCreate):
    data: str = HabrVacancyFields.data
    fingerprint: str = HabrVacancyFields.fingerprint
    link: HttpsUrl = HabrVacancyFields.link
    published_at: datetime = HabrVacancyFields.published_at
    external_id: int = HabrVacancyFields.external_id

    @computed_field  # type: ignore[prop-decorator]
    @property
    def source(self) -> SourceEnum:
        return SourceEnum.HABR

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return generate_vacancy_hash(self.external_id, SourceEnum.HABR)


class HabrVacancyRead(BaseVacancyRead):
    id: int = HabrVacancyFields.id
    hash: str = HabrVacancyFields.hash
    source: SourceEnum = HabrVacancyFields.source
    fingerprint: str = HabrVacancyFields.fingerprint
    link: HttpsUrl = HabrVacancyFields.link
    published_at: datetime = HabrVacancyFields.published_at
    external_id: int = HabrVacancyFields.external_id

    model_config = ConfigDict(from_attributes=True)
