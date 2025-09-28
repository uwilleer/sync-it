from collections.abc import Iterable, Sequence
from datetime import UTC, datetime

from common.shared.repositories import BaseRepository
from constants.fingerprint import FINGERPRINT_SIMILARITY_THRESHOLD
from database.models import Vacancy
from sqlalchemy import func, select, update


__all__ = ["BaseVacancyRepository"]


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

    async def get_last_vacancy(self) -> VacancyType | None:
        """Возвращает последнюю вакансию."""
        stmt = select(self.model).order_by(self.model.published_at.desc()).limit(1)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def find_duplicate_vacancy_hash_by_fingerprint(self, fingerprint: str) -> str | None:
        """Найти дубликат вакансии по содержимому."""
        stmt = (
            select(self.model.hash)
            .where(func.similarity(self.model.fingerprint, fingerprint) > FINGERPRINT_SIMILARITY_THRESHOLD)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, vacancy: VacancyType) -> VacancyType:
        self._session.add(vacancy)
        await self._session.flush()
        await self._session.refresh(vacancy)

        return vacancy

    async def update_published_at(self, vacancy_hash: str, published_at: datetime) -> bool:
        """Обновляет дату публикации вакансии напрямую через UPDATE."""
        stmt = (
            update(Vacancy).where(Vacancy.hash == vacancy_hash).values(published_at=published_at).returning(Vacancy.id)
        )
        result = await self._session.execute(stmt)
        updated = result.scalar_one_or_none()
        return updated is not None

    async def mark_as_processed(self, vacancy_hash: str) -> bool:
        """
        Помечает вакансию обработанной из первой подходящей таблицы по хешу.

        True - вакансия помечена как удаленная
        False - вакансия не найдена
        """
        # Только для удаления. Используем Vacancy, а не self._model
        stmt = (
            update(Vacancy)
            .where(Vacancy.hash == vacancy_hash)
            .values(processed_at=datetime.now(tz=UTC))
            .returning(Vacancy.processed_at)
        )
        result = await self._session.execute(stmt)
        processed_at = result.scalar_one_or_none()

        if processed_at is None:
            return False

        return processed_at is not None
