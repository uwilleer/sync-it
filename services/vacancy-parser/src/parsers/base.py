from abc import ABC, abstractmethod

from common.logger import get_logger
from unitofwork import UnitOfWork


__all__ = ["BaseParser"]


logger = get_logger(__name__)


class BaseParser[VacancyServiceType, VacancyCreateType](ABC):
    # Размер батча для загрузки вакансий
    BATCH_SIZE = 100

    def __init__(self, uow: UnitOfWork, service: VacancyServiceType) -> None:
        self.uow = uow
        self.service = service
        self.current_batch = 0

    @abstractmethod
    async def parse(self) -> None:
        """Основной метод парсинга каналов."""

    async def add_vacancy(self, new_vacancy: VacancyCreateType) -> None:
        self.current_batch += 1
        await self.service.add_vacancy(new_vacancy, with_refresh=False)  # type: ignore[attr-defined]
        logger.debug("Added vacancy %s", new_vacancy.link)  # type: ignore[attr-defined]

        if self.current_batch >= self.BATCH_SIZE:
            await self.uow.commit()
            self.current_batch = 0
            logger.debug("Commited batch for parser %", self.__class__.__name__)
