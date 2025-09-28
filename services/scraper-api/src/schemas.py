from pydantic import BaseModel


__all__ = ["TelegramChannelMessageSchema"]


class TelegramChannelMessageSchema(BaseModel):
    id: int
    datetime: str
    text: str
