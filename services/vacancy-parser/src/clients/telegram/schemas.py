from datetime import datetime

from pydantic import BaseModel


__all__ = [
    "TelegramChannelMessageSchema",
    "TelegramChannelMessagesResponse",
    "TelegramNewestMessagesRequest",
]


class TelegramNewestMessagesRequest(BaseModel):
    channel_username: str
    date_gte: datetime | None


class TelegramChannelMessageSchema(BaseModel):
    id: int
    datetime: datetime
    text: str


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
