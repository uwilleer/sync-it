from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import WorkFormat
from database.models.enums import WorkFormatEnum
from pydantic import BaseModel, ConfigDict


class WorkFormatFields(ModelFields):
    __model__ = WorkFormat

    id: int
    name: WorkFormatEnum
    vacancies: list[Any]


class WorkFormatCreate(BaseModel):
    name: WorkFormatEnum = WorkFormatFields.name


class WorkFormatRead(BaseModel):
    id: int = WorkFormatFields.id
    name: WorkFormatEnum = WorkFormatFields.name

    model_config = ConfigDict(from_attributes=True)
