from pydantic import BaseModel, Field
from schemas import DateGTEUTCMixin, TelegramChannelMessageSchema


class TelegramVacanciesQuery(DateGTEUTCMixin):
    channel_username: str = Field(description="Username телеграм канала")
    topic_id: int | None = Field(None, description="ID топика телеграм канала")


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
