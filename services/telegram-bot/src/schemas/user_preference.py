from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import UserPreference
from database.models.enums import PreferencesCategoryCodeEnum
from pydantic import BaseModel, ConfigDict


class UserPreferenceFields(ModelFields):
    __model__ = UserPreference

    id: int
    user_id: int
    user: Any
    category_code: PreferencesCategoryCodeEnum
    item_id: int
    item_name: str


class UserPreferenceCreate(BaseModel):
    user_id: int = UserPreferenceFields.user_id
    category_code: PreferencesCategoryCodeEnum = UserPreferenceFields.category_code
    item_id: int = UserPreferenceFields.item_id
    item_name: str = UserPreferenceFields.item_name


class UserPreferenceRead(BaseModel):
    id: int = UserPreferenceFields.id
    user_id: int = UserPreferenceFields.user_id
    category_code: PreferencesCategoryCodeEnum = UserPreferenceFields.category_code
    item_id: int = UserPreferenceFields.item_id
    item_name: str = UserPreferenceFields.item_name

    model_config = ConfigDict(from_attributes=True)
