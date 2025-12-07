from datetime import datetime

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    status: str = "pong"


class TelegramDetailedMessageParams(BaseModel):
    before: int


class HabrVacancyPublishedDateSchema(BaseModel):
    date: datetime


class HabrVacancySchema(BaseModel):
    id: int
    published_date: HabrVacancyPublishedDateSchema = Field(alias="publishedDate")


class HabrVacancyMetaSchema(BaseModel):
    total_pages: int = Field(alias="totalPages")


class HabrVacancyDetailResponse(BaseModel):
    pass


class HabrVacancyListResponse(BaseModel):
    list: list[HabrVacancySchema]
    meta: HabrVacancyMetaSchema
