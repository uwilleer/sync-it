from abc import ABC, abstractmethod
from typing import List

from common.logger import get_logger
from unitofwork import UnitOfWork
from constants.fingerprint import FINGERPRINT_SIMILARITY_THRESHOLD


__all__ = ["BaseParser"]


logger = get_logger(__name__)


class BaseParser[VacancyServiceType, VacancyCreateType](ABC):
    # Размер батча для загрузки вакансий
    BATCH_SIZE = 20

    def __init__(self, uow: UnitOfWork, service: VacancyServiceType) -> None:
        self.uow = uow
        self.service = service
        self._vacancies_batch: list[VacancyCreateType] = []

    @abstractmethod
    async def parse(self) -> None:
        """Основной метод парсинга каналов."""

    async def add_vacancy(self, new_vacancy: VacancyCreateType) -> None:
        self._vacancies_batch.append(new_vacancy)
        logger.debug("Added vacancy %s", new_vacancy.link)  # type: ignore[attr-defined]

        if len(self._vacancies_batch) >= self.BATCH_SIZE:
            await self.save_vacancies()

    async def save_vacancies(self) -> None:
        if not self._vacancies_batch:
            return

        # Убираем дубликаты внутри текущего батча по схожести fingerprint.
        deduped_batch: List[VacancyCreateType] = self._deduplicate_batch(self._vacancies_batch)

        await self.service.add_vacancies_bulk(deduped_batch)  # type: ignore[attr-defined]
        logger.info(
            "Committed %d (from %d) vacancies for parser %s",
            len(deduped_batch),
            len(self._vacancies_batch),
            self.__class__.__name__,
        )
        self._vacancies_batch = []

    def _deduplicate_batch(self, vacancies: list[VacancyCreateType]) -> list[VacancyCreateType]:
        """Удаляет дубликаты внутри одного батча по схожести fingerprint.

        Если найдены несколько очень похожих вакансий, оставляет первую и
        обновляет у неё поле published_at на максимальное из объединяемых.
        """
        if len(vacancies) <= 1:
            return vacancies

        def trigrams(s: str) -> set[str]:
            if len(s) < 3:
                return {s} if s else set()
            return {s[i : i + 3] for i in range(len(s) - 2)}

        def trigram_similarity(a: str, b: str) -> float:
            ta = trigrams(a)
            tb = trigrams(b)
            if not ta and not tb:
                return 1.0
            if not ta or not tb:
                return 0.0
            intersection = len(ta & tb)
            # Dice coefficient — близко к pg_trgm similarity
            return (2.0 * intersection) / (len(ta) + len(tb))

        result: list[VacancyCreateType] = []

        for candidate in vacancies:
            is_duplicate = False
            for kept in result:
                similarity = trigram_similarity(
                    str(getattr(candidate, "fingerprint")), str(getattr(kept, "fingerprint"))
                )
                if similarity > FINGERPRINT_SIMILARITY_THRESHOLD:
                    # Считаем дубликатом: переносим максимальную дату публикации к сохранённому экземпляру
                    cand_dt = getattr(candidate, "published_at")
                    kept_dt = getattr(kept, "published_at")
                    if cand_dt > kept_dt:
                        setattr(kept, "published_at", cand_dt)
                    is_duplicate = True
                    break

            if not is_duplicate:
                result.append(candidate)

        if len(result) != len(vacancies):
            logger.debug(
                "Deduplicated batch: %d -> %d items for parser %s",
                len(vacancies),
                len(result),
                self.__class__.__name__,
            )

        return result
