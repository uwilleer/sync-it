from pydantic import BaseModel, ConfigDict, Field
from schemas import DateGTEUTCMixin, TelegramChannelMessageSchema


class TelegramVacanciesQuery(DateGTEUTCMixin):
    channel_username: str = Field(description="Username телеграм канала")
    channel_topic_id: int | None = Field(None, description="ID топика телеграм канала")

    model_config = ConfigDict(extra="forbid")


class TelegramChannelMessagesResponse(BaseModel):
    messages: list[TelegramChannelMessageSchema]
