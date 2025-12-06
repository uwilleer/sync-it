from clients.base import BaseParserClient
from clients.schemas import PingResponse, TelegramDetailedMessageParams
from common.logger import get_logger
from common.shared.decorators.concurency import limit_requests
from httpx import URL
from parsers import TelegramParser
from schemas import TelegramChannelMessageSchema


logger = get_logger(__name__)


class TelegramClient(BaseParserClient):
    url = URL("https://t.me")
    parser = TelegramParser

    async def ping(self) -> PingResponse:
        url = f"{self.url}/telegram"
        response = await self.client.get(url)
        response.raise_for_status()

        return PingResponse()

    async def get_newest_message_id(self, channel_username: str) -> int | None:
        url = f"{self.url}/s/{channel_username}"
        response = await self.client.get(url)

        if response.is_redirect:
            logger.debug("Channel %s is private or does not exist")
            return None

        response.raise_for_status()

        return self.parser.parse_message_id(response.text)

    @limit_requests(20)
    async def get_detailed_message(self, channel_username: str, message_id: int) -> TelegramChannelMessageSchema | None:
        url = f"{self.url}/s/{channel_username}/{message_id}"

        # +1 т.к. надо подгрузить до переданного message_id
        params_model = TelegramDetailedMessageParams(before=message_id + 1)

        response = await self.client.get(url, params=params_model.model_dump())
        response.raise_for_status()

        return self.parser.parse_detailed_message(response.text, channel_username, message_id)


telegram_client = TelegramClient()
