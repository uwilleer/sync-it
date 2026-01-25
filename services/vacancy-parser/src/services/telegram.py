from datetime import datetime

from repositories import TelegramVacancyRepository
from schemas.vacancy import TelegramVacancyCreate, TelegramVacancyRead

from services import BaseVacancyService


__all__ = ["TelegramVacancyService"]


class TelegramVacancyService(BaseVacancyService[TelegramVacancyRead, TelegramVacancyCreate, TelegramVacancyRepository]):
    """Сервис для бизнес-логики, связанной с вакансиями из Телеграма."""

    read_schema = TelegramVacancyRead
    create_schema = TelegramVacancyCreate
    repo: "TelegramVacancyRepository"

    def _get_repo(self) -> "TelegramVacancyRepository":
        return self._uow.tg_vacancies

    async def get_last_vacancy_published_at(self, username: str) -> datetime | None:
        return await self.repo.get_last_published_at(username)
