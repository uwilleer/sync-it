from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:  # noqa: B903 Class could be dataclass or namedtuple
    """Базовый репозиторий для работы с базой данных."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
