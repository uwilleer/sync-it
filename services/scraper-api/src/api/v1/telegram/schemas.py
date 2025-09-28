from pydantic import BaseModel
from schemas import TelegramChannelMessageSchema


__all__ = ["TelegramChannelMessagesResponse"]


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
