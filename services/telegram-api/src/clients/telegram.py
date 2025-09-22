import asyncio

from clients.schemas import TelegramDetailedMessageParams, TelegramPingResponse
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests
from httpx import URL
from parsers import TelegramParser
from schemas import ChannelMessageSchema


__all__ = ["telegram_client"]


logger = get_logger(__name__)


class _TelegramClient(BaseClient):
    url = URL("https://t.me")
    _parser = TelegramParser

    async def ping(self) -> TelegramPingResponse:
        url = f"{self.url}/telegram"
        response = await self.client.get(url)
        response.raise_for_status()

        return TelegramPingResponse()

    async def get_newest_message_id(self, channel_username: str) -> int | None:
        url = f"{self.url}/s/{channel_username}"
        response = await self.client.get(url)

        if response.is_redirect:
            logger.debug("Channel %s is private or does not exist")
            return None

        response.raise_for_status()

        return TelegramParser.parse_message_id(response.text)

    @limit_requests(25)
    async def get_detailed_message(self, channel_username: str, message_id: int) -> ChannelMessageSchema | None:
        url = f"{self.url}/s/{channel_username}/{message_id}"

        # +1 т.к. надо подгрузить до переданного message_id
        params_model = TelegramDetailedMessageParams(before=message_id + 1)

        response = await self.client.get(url, params=params_model.model_dump())
        response.raise_for_status()

        return TelegramParser.parse_detailed_message(response.text, channel_username, message_id)

    async def get_detailed_messages_by_message_ids(
        self, channel_username: str, message_ids: list[int]
    ) -> list[ChannelMessageSchema]:
        tasks = [self.get_detailed_message(channel_username, message_id) for message_id in message_ids]
        results: list[ChannelMessageSchema | BaseException | None] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        messages: list[ChannelMessageSchema] = []
        for result in results:
            if isinstance(result, BaseException):
                logger.error("Failed to get message", exc_info=result)
                continue

            if result:
                messages.append(result)

        return messages


telegram_client = _TelegramClient()
