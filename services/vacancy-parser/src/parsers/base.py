from abc import ABC, abstractmethod

from common.logger import get_logger
from unitofwork import UnitOfWork


__all__ = ["BaseParser"]


logger = get_logger(__name__)


class BaseParser[VacancyServiceType, VacancyCreateType](ABC):
    # Размер батча для загрузки вакансий
    BATCH_SIZE = 20

    def __init__(self, uow: UnitOfWork, service: VacancyServiceType) -> None:
        self.uow = uow
        self.service = service
        self._vacancies_batch: list[VacancyCreateType] = []
        self._processed_fingerprints: set[str] = set()

    @abstractmethod
    async def parse(self) -> None:
        """Основной метод парсинга каналов."""

    async def add_vacancy(self, new_vacancy: VacancyCreateType) -> None:
        if new_vacancy.fingerprint in self._processed_fingerprints:  # type: ignore[attr-defined]
            logger.debug("Fingerprint already processed")
            return
        self._processed_fingerprints.add(new_vacancy.fingerprint)  # type: ignore[attr-defined]

        self._vacancies_batch.append(new_vacancy)
        logger.debug("Added vacancy %s", new_vacancy.link)  # type: ignore[attr-defined]

        if len(self._vacancies_batch) >= self.BATCH_SIZE:
            await self.save_vacancies()

    async def save_vacancies(self) -> None:
        if not self._vacancies_batch:
            return

        await self.service.add_vacancies_bulk(self._vacancies_batch)  # type: ignore[attr-defined]
        logger.info("Commited batch of %d vacancies for parser %s", len(self._vacancies_batch), self.__class__.__name__)
        self._vacancies_batch = []
