from datetime import datetime

from pydantic import BaseModel


class TelegramNewestMessagesRequest(BaseModel):
    channel_username: str
    channel_topic_id: int | None
    date_gte: datetime | None


class TelegramChannelMessageSchema(BaseModel):
    id: int
    datetime: datetime
    text: str


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
