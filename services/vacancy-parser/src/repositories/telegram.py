from typing import TYPE_CHECKING

from database.models import TelegramVacancy
from repositories import BaseVacancyRepository
from sqlalchemy import func, select


__all__ = ["TelegramVacancyRepository"]


if TYPE_CHECKING:
    from parsers.schemas import TelegramChannelUrl


class TelegramVacancyRepository(BaseVacancyRepository[TelegramVacancy]):
    _model = TelegramVacancy

    async def get_last_message_id(self, link: "TelegramChannelUrl") -> int | None:
        """Получить последний message_id для заданного Telegram канала."""
        smtp = select(func.max(self._model.message_id)).where(self._model.channel_username == link.channel_username)
        result = await self._session.execute(smtp)
        return result.scalar_one_or_none()
