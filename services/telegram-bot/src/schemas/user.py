from datetime import datetime

from pydantic import BaseModel, ConfigDict
from schemas.user_preference import UserPreferenceRead


class BaseUser(BaseModel):
    telegram_id: int

    username: str | None
    first_name: str
    last_name: str | None


class UserCreate(BaseUser):
    pass


class UserRead(BaseUser):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()


class UserWithPreferences(UserRead):
    preferences: list[UserPreferenceRead]
