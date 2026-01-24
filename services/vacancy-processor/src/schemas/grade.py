from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import Grade
from database.models.enums import GradeEnum
from pydantic import BaseModel, ConfigDict


class GradeFields(ModelFields):
    __model__ = Grade

    id: int
    name: GradeEnum
    vacancies: list[Any]


class GradeCreate(BaseModel):
    name: GradeEnum = GradeFields.name


class GradeRead(BaseModel):
    id: int = GradeFields.id
    name: GradeEnum = GradeFields.name

    model_config = ConfigDict(from_attributes=True)
