from typing import TYPE_CHECKING

from repositories import TelegramVacancyRepository
from schemas.vacancies import TelegramVacancyCreate, TelegramVacancyRead

from services import BaseVacancyService


if TYPE_CHECKING:
    from parsers.schemas import TelegramChannelUrl


__all__ = ["TelegramVacancyService"]


class TelegramVacancyService(BaseVacancyService[TelegramVacancyRead, TelegramVacancyCreate, TelegramVacancyRepository]):
    """Сервис для бизнес-логики, связанной с вакансиями из Телеграма."""

    read_schema = TelegramVacancyRead
    create_schema = TelegramVacancyCreate
    repo: "TelegramVacancyRepository"

    def _get_repo(self) -> "TelegramVacancyRepository":
        return self._uow.tg_vacancies

    async def get_last_message_id(self, link: "TelegramChannelUrl") -> int | None:
        return await self.repo.get_last_message_id(link)
