from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field, field_validator


__all__ = [
    "DateGTEUTCMixin",
    "HabrDetailedVacancySchema",
    "TelegramChannelMessageSchema",
]


def _get_default_date_gte() -> datetime:
    start = datetime.now(UTC) - timedelta(days=30)

    return start.replace(hour=0, minute=0, second=0, microsecond=0)


class DateGTEUTCMixin(BaseModel):
    date_gte: datetime = Field(
        _get_default_date_gte(),
        description="Datetime in UTC, format: YYYY-MM-DDTHH:MM:SSZ or +00:00",
    )

    @field_validator("date_gte", mode="after")
    @classmethod
    def must_be_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("Datetime must include timezone and be in UTC (e.g. 2025-09-28T15:30:00Z)")
        if v.utcoffset() != UTC.utcoffset(v):
            raise ValueError("Timezone must be UTC (use Z or +00:00)")
        return v.astimezone(UTC)


class TelegramChannelMessageSchema(BaseModel):
    id: int
    datetime: datetime
    text: str


class HabrDetailedVacancySchema(BaseModel):
    id: int
    datetime: datetime
    text: str
