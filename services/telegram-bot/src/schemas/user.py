from datetime import datetime
from typing import Any

from common.shared.schemas.model import ModelFields
from database.models import User
from pydantic import BaseModel, ConfigDict
from schemas.user_preference import UserPreferenceRead


class UserFields(ModelFields):
    __model__ = User

    id: int
    telegram_id: int
    username: str | None
    first_name: str
    last_name: str | None
    created_at: datetime
    last_active_at: datetime
    preferences: list[Any]


class UserCreate(BaseModel):
    telegram_id: int = UserFields.telegram_id
    username: str | None = UserFields.username
    first_name: str = UserFields.first_name
    last_name: str | None = UserFields.last_name


class UserRead(BaseModel):
    id: int = UserFields.id
    telegram_id: int = UserFields.telegram_id
    username: str | None = UserFields.username
    first_name: str = UserFields.first_name
    last_name: str | None = UserFields.last_name
    created_at: datetime = UserFields.created_at

    model_config = ConfigDict(from_attributes=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()


class UserWithPreferences(UserRead):
    preferences: list[UserPreferenceRead]
