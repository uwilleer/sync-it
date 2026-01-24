from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import Profession
from database.models.enums import ProfessionEnum
from pydantic import BaseModel, ConfigDict


class ProfessionFields(ModelFields):
    __model__ = Profession

    id: int
    name: ProfessionEnum
    vacancies: list[Any]


class ProfessionCreate(BaseModel):
    name: ProfessionEnum = ProfessionFields.name


class ProfessionRead(BaseModel):
    id: int = ProfessionFields.id
    name: ProfessionEnum = ProfessionFields.name

    model_config = ConfigDict(from_attributes=True)
