from repositories import VacancyRepository
from schemas.vacancies import VacancyRead
from schemas.vacancies.vacancy import VacancyCreate

from services import BaseVacancyService


__all__ = ["VacancyService"]


class VacancyService(BaseVacancyService[VacancyRead, VacancyCreate, VacancyRepository]):
    read_schema = VacancyRead
    create_schema = VacancyCreate
    repo: "VacancyRepository"

    def _get_repo(self) -> "VacancyRepository":
        return self._uow.vacancies

    async def cleanup_duplicates_by_fingerprint(self, limit: int | None = None) -> int:
        """Удаляет дубли вакансий по fingerprint и фиксирует транзакцию."""
        deleted = await self.repo.cleanup_duplicates_by_fingerprint(limit=limit)
        await self.commit()
        return deleted
