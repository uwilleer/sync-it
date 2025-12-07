from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from common.database.engine import async_session_factory
from common.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


logger = get_logger(__name__)


class BaseUnitOfWork(ABC):
    """Базовый класс реализация Unit Of Work."""

    # Защищает от повторного входа в контекстный менеджер
    _is_context_active: bool = False

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] = async_session_factory) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        if self._is_context_active:
            raise RuntimeError("UoW is already active")

        self._session = self._session_factory()

        self.init_repositories()

        self._is_context_active = True

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type:
                await self.rollback()
        finally:
            await self._session.close()

    @abstractmethod
    def init_repositories(self) -> None:
        """Инициализирует репозитории для экземпляра UoW."""

    async def commit(self) -> None:
        """Сохраняет все изменения в рамках текущей транзакции."""
        await self._session.commit()
        logger.debug("Session commited")

    async def rollback(self) -> None:
        """Откатывает все изменения в рамках текущей транзакции."""
        await self._session.rollback()
        logger.debug("Session rolled back")
