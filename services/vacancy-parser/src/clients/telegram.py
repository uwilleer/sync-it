from clients.schemas import TelegramChannelMessageSchema, TelegramChannelMessagesResponse, TelegramNewestMessagesRequest
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


__all__ = ["telegram_client"]


class _TelegramClient(BaseClient):
    url = build_service_url(ServiceEnum.TELEGRAM_API, "/api/v1/channel")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 30

    async def get_newest_messages(
        self, channel_username: str, after_message_id: int | None = None
    ) -> list[TelegramChannelMessageSchema]:
        url = f"{self.url}/{channel_username}/messages"
        params = TelegramNewestMessagesRequest(after_message_id=after_message_id)

        response = await self.client.get(url, params=params.model_dump(exclude_none=True))
        response.raise_for_status()

        data = response.json()
        model_response = TelegramChannelMessagesResponse.model_validate(data)

        return model_response.messages


telegram_client = _TelegramClient()
