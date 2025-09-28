from datetime import datetime

from pydantic import BaseModel


__all__ = [
    "HabrDetailedVacancySchema",
    "TelegramChannelMessageSchema",
]


class TelegramChannelMessageSchema(BaseModel):
    id: int
    datetime: datetime
    text: str


class HabrDetailedVacancySchema(BaseModel):
    id: int
    datetime: datetime
    text: str
