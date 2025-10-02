from collections.abc import Iterable, Sequence
from datetime import UTC, datetime

from common.logger import get_logger
from common.shared.repositories import BaseRepository
from constants.fingerprint import FINGERPRINT_SIMILARITY_THRESHOLD
from database.models import Vacancy
from sqlalchemy import Text, cast, func, select, update


__all__ = ["BaseVacancyRepository"]


logger = get_logger(__name__)


class BaseVacancyRepository[VacancyType: Vacancy](BaseRepository):
    """Базовый репозиторий для работы с моделями вакансий."""

    model: type[VacancyType]

    async def get_recent_vacancies(self, limit: int = 100) -> Sequence[VacancyType]:
        """Возвращает последние актуальные вакансии."""
        stmt = (
            select(self.model)
            .where(self.model.processed_at.is_(None))
            .order_by(self.model.published_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_existing_hashes(self, hashes: Iterable[str]) -> set[str]:
        """Возвращает set уже существующих хешей в БД."""
        stmt = select(self.model.hash).where(self.model.hash.in_(hashes))
        result = await self._session.execute(stmt)

        return set(result.scalars().all())

    async def find_duplicate_vacancy_hash_by_fingerprint(self, fingerprint: str) -> str | None:
        """Найти дубликат вакансии по содержимому."""
        stmt = (
            select(self.model.hash)
            .where(self.model.fingerprint.op("%")(cast(fingerprint, Text)))
            .where(func.similarity(self.model.fingerprint, cast(fingerprint, Text)) > FINGERPRINT_SIMILARITY_THRESHOLD)
            .limit(1)
        )
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def add_bulk(self, vacancies: Sequence[VacancyType]) -> None:
        """
        Добавляет сразу несколько вакансий.
        Возвращает количество реально вставленных строк.
        """
        self._session.add_all(vacancies)

    async def update_published_at(self, vacancy_hash: str, published_at: datetime) -> bool:
        """Обновляет дату публикации вакансии напрямую через UPDATE."""
        stmt = (
            update(Vacancy).where(Vacancy.hash == vacancy_hash).values(published_at=published_at).returning(Vacancy.id)
        )
        result = await self._session.execute(stmt)
        updated = result.scalar_one_or_none()

        return updated is not None

    async def mark_as_processed_bulk(self, vacancy_hashes: list[str]) -> None:
        """
        Помечает сразу несколько вакансий как обработанные.
        Возвращает количество обновленных строк.
        """
        if not vacancy_hashes:
            return

        stmt = (
            update(Vacancy)
            .where(Vacancy.processed_at.is_(None), Vacancy.hash.in_(vacancy_hashes))
            .values(processed_at=datetime.now(tz=UTC))
        )
        await self._session.execute(stmt)
