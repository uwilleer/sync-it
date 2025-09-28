from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from common.shared.services import BaseUOWService
from schemas.vacancies import BaseVacancyCreate, BaseVacancyRead
from unitofwork import UnitOfWork


if TYPE_CHECKING:
    from repositories import BaseVacancyRepository


__all__ = ["BaseVacancyService"]


class BaseVacancyService[
    VacancyReadType: BaseVacancyRead,
    VacancyCreateType: BaseVacancyCreate,
    VacancyRepositoryType: BaseVacancyRepository[Any],  # Головная боль без Any
](BaseUOWService[UnitOfWork], ABC):
    read_schema: type[VacancyReadType]
    create_schema: type[VacancyCreateType]
    repo: "VacancyRepositoryType"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.repo = self._get_repo()

    @abstractmethod
    def _get_repo(self) -> "VacancyRepositoryType":
        pass

    async def find_duplicate_vacancy_by_fingerprint(self, fingerprint: str) -> str | None:
        return await self.repo.find_duplicate_vacancy_hash_by_fingerprint(fingerprint)

    async def get_existing_hashes(self, hashes: Iterable[str]) -> set[str]:
        return await self.repo.get_existing_hashes(hashes)

    async def get_recent_vacancies(self, limit: int = 100) -> list[VacancyReadType]:
        """Получает последние актуальные вакансии из всех источников."""
        vacancies = await self.repo.get_recent_vacancies(limit=limit)
        return [self.read_schema.model_validate(v) for v in vacancies]

    async def update_vacancy_published_at(self, vacancy_hash: str, published_at: datetime) -> bool:
        """Обновляет дату публикации вакансии по её хэшу."""
        return await self.repo.update_published_at(vacancy_hash, published_at)

    async def mark_as_processed(self, vacancy_hash: str) -> bool:
        """Помечает вакансию как обработанную по её хешу."""
        return await self.repo.mark_as_processed(vacancy_hash=vacancy_hash)

    async def add_vacancy(self, vacancy: VacancyCreateType) -> VacancyReadType:
        vacancy_model = self.repo.model(**vacancy.model_dump())
        created_vacancy = await self.repo.add(vacancy_model)

        return self.read_schema.model_validate(created_vacancy)
