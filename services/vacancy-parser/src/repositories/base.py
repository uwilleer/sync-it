from collections.abc import Iterable, Sequence
from datetime import UTC, datetime

from common.shared.repositories import BaseRepository
from constants.fingerprint import FINGERPRINT_SIMILARITY_THRESHOLD
from database.models import Vacancy
from sqlalchemy import func, select, update


__all__ = ["BaseVacancyRepository"]


class BaseVacancyRepository[VacancyType: Vacancy](BaseRepository):
    """Базовый репозиторий для работы с моделями вакансий."""

    _model: type[VacancyType]

    async def get_recent_vacancies(self, limit: int = 100) -> Sequence[VacancyType]:
        """Получить последние актуальные вакансии."""
        stmt = (
            select(self._model)
            .where(self._model.processed_at.is_(None))
            .order_by(self._model.published_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_existing_hashes(self, hashes: Iterable[str]) -> set[str]:
        """Получить set уже существующих хешей в БД."""
        stmt = select(self._model.hash).where(self._model.hash.in_(hashes))
        result = await self._session.execute(stmt)

        return set(result.scalars().all())

    async def find_duplicate_vacancy_by_fingerprint(self, fingerprint: str) -> VacancyType | None:
        """Найти дубликат вакансии по содержимому."""
        stmt = (
            select(self._model)
            .where(func.similarity(self._model.fingerprint, fingerprint) > FINGERPRINT_SIMILARITY_THRESHOLD)
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
        """Обновляет дату публикации вакансии."""
        # Только для обновления. Используем Vacancy, а не self._model
        stmt = select(Vacancy).where(Vacancy.hash == vacancy_hash).with_for_update()
        result = await self._session.execute(stmt)
        vacancy = result.scalar_one_or_none()
        if not vacancy:
            return False

        vacancy.published_at = published_at
        return True

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
