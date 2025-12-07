import base64
from datetime import UTC, datetime
import pathlib

from clients.telethon.exceptions import TelethonNotAuthorizedError
from common.logger import get_logger
from core.config import service_config
from schemas import TelegramChannelMessageSchema
from telethon import TelegramClient  # type: ignore[import-untyped]


logger = get_logger(__name__)


session_bytes = base64.b64decode(service_config.telethon_session_base64)
session_file = f"{service_config.telethon_session_name}.session"
with pathlib.Path(session_file).open("wb") as f:
    f.write(session_bytes)


class TelethonClient:
    def __init__(self, client: TelegramClient) -> None:
        self._client = client
        self._is_started = False

    @property
    def client(self) -> TelegramClient:
        if not self._is_started:
            raise RuntimeError("TelethonClient is not started")

        return self._client

    async def start(self) -> None:
        if not self._is_started:
            try:
                await self._client.start()
                self._is_started = True
            except EOFError as e:
                raise TelethonNotAuthorizedError("Не удалось найти активную сессию telethon") from e

    async def stop(self) -> None:
        if self._is_started:
            await self._client.disconnect()
            self._is_started = False

    async def get_detailed_messages(
        self, date_gte: datetime, channel_username: str, topic_id: int
    ) -> list[TelegramChannelMessageSchema]:
        channel = await self.client.get_entity(channel_username)

        result: list[TelegramChannelMessageSchema] = []

        async for message in self.client.iter_messages(channel, reply_to=topic_id):
            message_datetime = message.date.astimezone(UTC)

            if message_datetime < date_gte:
                break

            result.append(
                TelegramChannelMessageSchema(
                    id=message.id,
                    datetime=message_datetime,
                    text=message.message.strip(),
                )
            )

        return result


telethon_client = TelethonClient(
    TelegramClient(
        service_config.telethon_session_name,
        service_config.telethon_api_id,
        service_config.telethon_api_hash,
    )
)
