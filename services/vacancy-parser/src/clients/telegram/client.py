from datetime import datetime

from clients.telegram.schemas import (
    TelegramChannelMessageSchema,
    TelegramChannelMessagesResponse,
    TelegramNewestMessagesRequest,
)
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient


logger = get_logger(__name__)


class TelegramClient(BaseClient):
    url = build_service_url(ServiceEnum.SCRAPER_API, "/api/v1/telegram/messages")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 60

    async def get_newest_messages(
        self, channel_username: str, channel_topic_id: int | None = None, date_gte: datetime | None = None
    ) -> list[TelegramChannelMessageSchema]:
        # FIXME
        params = TelegramNewestMessagesRequest(
            channel_username=channel_username,
            channel_topic_id=channel_topic_id,
            date_gte=date_gte,
        )

        response = await self.client.get(self.url, params=params.model_dump(exclude_none=True))
        response.raise_for_status()

        data = response.json()
        model_response = TelegramChannelMessagesResponse.model_validate(data)

        logger.debug("Got %s new messages for channel %s", len(model_response.messages), channel_username)

        return model_response.messages


telegram_client = TelegramClient()
