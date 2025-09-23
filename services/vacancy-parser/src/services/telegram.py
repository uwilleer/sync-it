from typing import TYPE_CHECKING

from database.models import TelegramVacancy
from repositories import TelegramVacancyRepository
from schemas.vacancy import TelegramVacancyCreate, TelegramVacancyRead

from services import BaseVacancyService


__all__ = ["TelegramVacancyService"]


if TYPE_CHECKING:
    from parsers.schemas import TelegramChannelUrl


class TelegramVacancyService(BaseVacancyService[TelegramVacancyRead, TelegramVacancyCreate, TelegramVacancyRepository]):
    """Сервис для бизнес-логики, связанной с вакансиями из Телеграма."""

    _read_schema = TelegramVacancyRead
    _create_schema = TelegramVacancyCreate
    _repo: "TelegramVacancyRepository"

    def _get_repo(self) -> "TelegramVacancyRepository":
        return self._uow.tg_vacancies

    async def get_last_message_id(self, link: "TelegramChannelUrl") -> int | None:
        return await self._repo.get_last_message_id(link)

    async def add_vacancy(self, vacancy: TelegramVacancyCreate) -> TelegramVacancyRead:
        vacancy_model = TelegramVacancy(**vacancy.model_dump())
        created_vacancy = await self._repo.add(vacancy_model)

        return self._read_schema.model_validate(created_vacancy)
