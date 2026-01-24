from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import Skill
from database.models.enums import SkillEnum
from pydantic import BaseModel, ConfigDict


class SkillFields(ModelFields):
    __model__ = Skill

    id: int
    name: SkillEnum
    vacancies: list[Any]


class SkillCreate(BaseModel):
    name: SkillEnum = SkillFields.name


class SkillRead(BaseModel):
    id: int = SkillFields.id
    name: SkillEnum = SkillFields.name

    model_config = ConfigDict(from_attributes=True)
