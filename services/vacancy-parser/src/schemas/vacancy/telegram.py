from datetime import datetime

from common.shared.schemas.http import HttpsUrl
from database.models import TelegramVacancy
from database.models.enums import SourceEnum
from pydantic import ConfigDict, computed_field
from schemas.vacancy import BaseVacancyCreate, BaseVacancyRead, VacancyFields
from utils import generate_vacancy_hash


class TelegramVacancyFields(VacancyFields):
    __model__ = TelegramVacancy

    channel_username: str


class TelegramVacancyCreate(BaseVacancyCreate):
    data: str = TelegramVacancyFields.data
    channel_username: str = TelegramVacancyFields.channel_username
    fingerprint: str = TelegramVacancyFields.fingerprint
    link: HttpsUrl = TelegramVacancyFields.link
    published_at: datetime = TelegramVacancyFields.published_at

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return generate_vacancy_hash(str(self.link), SourceEnum.TELEGRAM)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def source(self) -> SourceEnum:
        return SourceEnum.TELEGRAM


class TelegramVacancyRead(BaseVacancyRead):
    id: int = TelegramVacancyFields.id
    hash: str = TelegramVacancyFields.hash
    fingerprint: str = TelegramVacancyFields.fingerprint
    link: HttpsUrl = TelegramVacancyFields.link
    published_at: datetime = TelegramVacancyFields.published_at
    source: SourceEnum = TelegramVacancyFields.source
    channel_username: str = TelegramVacancyFields.channel_username

    model_config = ConfigDict(from_attributes=True)
