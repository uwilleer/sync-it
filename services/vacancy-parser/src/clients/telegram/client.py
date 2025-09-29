from clients.telegram.schemas import (
    TelegramChannelMessageSchema,
    TelegramChannelMessagesResponse,
    TelegramNewestMessagesRequest,
)
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient


__all__ = ["telegram_client"]


logger = get_logger(__name__)


class _TelegramClient(BaseClient):
    url = build_service_url(ServiceEnum.SCRAPER_API, "/api/v1/telegram/channel")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 30

    async def get_newest_messages(
        self, channel_username: str, after_message_id: int | None = None
    ) -> list[TelegramChannelMessageSchema]:
        logger.debug("Getting telegram newest messages from %s after %s message_id", channel_username, after_message_id)
        url = f"{self.url}/{channel_username}/messages"
        params = TelegramNewestMessagesRequest(after_message_id=after_message_id)

        response = await self.client.get(url, params=params.model_dump(exclude_none=True))
        response.raise_for_status()

        data = response.json()
        model_response = TelegramChannelMessagesResponse.model_validate(data)

        logger.debug("Got %s new messages for channel %s", len(model_response.messages), channel_username)

        return model_response.messages


telegram_client = _TelegramClient()
