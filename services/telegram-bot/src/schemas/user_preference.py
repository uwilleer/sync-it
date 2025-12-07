from database.models.enums import PreferencesCategoryCodeEnum
from pydantic import BaseModel, ConfigDict


class UserPreferenceBase(BaseModel):
    user_id: int
    category_code: PreferencesCategoryCodeEnum
    item_id: int
    item_name: str


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceRead(UserPreferenceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
