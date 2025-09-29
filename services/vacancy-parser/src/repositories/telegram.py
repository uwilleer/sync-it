from datetime import datetime

from database.models import TelegramVacancy
from repositories import BaseVacancyRepository
from sqlalchemy import func, select


__all__ = ["TelegramVacancyRepository"]


class TelegramVacancyRepository(BaseVacancyRepository[TelegramVacancy]):
    model = TelegramVacancy

    async def get_last_published_at(self, channel_username: str) -> datetime | None:
        """Получить последний message_id для заданного Telegram канала."""
        stmt = select(func.max(self.model.published_at)).where(self.model.channel_username == channel_username)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()
