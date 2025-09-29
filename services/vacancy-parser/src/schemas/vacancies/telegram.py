from database.models.enums import SourceEnum
from pydantic import computed_field
from schemas.vacancies import BaseVacancy, BaseVacancyCreate, BaseVacancyRead
from utils import generate_vacancy_hash


__all__ = [
    "TelegramVacancyCreate",
    "TelegramVacancyRead",
]


class BaseTelegramVacancy(BaseVacancy):
    source: SourceEnum = SourceEnum.TELEGRAM
    channel_username: str
    message_id: int


class TelegramVacancyCreate(BaseTelegramVacancy, BaseVacancyCreate):
    data: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return generate_vacancy_hash(f"{self.link}:{self.message_id}", SourceEnum.TELEGRAM)


class TelegramVacancyRead(BaseTelegramVacancy, BaseVacancyRead):
    pass
