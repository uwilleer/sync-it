from pydantic import BaseModel, Field
from schemas import DateGTEUTCMixin, TelegramChannelMessageSchema


__all__ = [
    "TelegramChannelMessagesResponse",
    "TelegramVacanciesQuery",
]


class TelegramVacanciesQuery(DateGTEUTCMixin):
    channel_username: str = Field(description="Username телеграм канала")


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
