from typing import Literal, overload

from common.shared.services import BaseUOWService
from database.models import User
from schemas.user import UserCreate, UserRead, UserWithPreferences
from unitofwork import UnitOfWork


__all__ = ["UserService"]


class UserService(BaseUOWService[UnitOfWork]):
    @overload
    async def get_by_telegram_id(self, telegram_id: int, *, with_preferences: Literal[True]) -> UserWithPreferences: ...
    @overload
    async def get_by_telegram_id(self, telegram_id: int, *, with_preferences: Literal[False] = False) -> UserRead: ...
    async def get_by_telegram_id(
        self, telegram_id: int, *, with_preferences: bool = False
    ) -> UserRead | UserWithPreferences:
        user = await self._uow.users.get_by_telegram_id(telegram_id, with_preferences=with_preferences)

        if with_preferences:
            return UserWithPreferences.model_validate(user)

        return UserRead.model_validate(user)

    async def add_user(self, user: UserCreate) -> UserRead:
        """Получает пользователя по telegram_id. Если его нет, создает нового."""
        user_model = User(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        created_user = await self._uow.users.add(user_model)

        return UserRead.model_validate(created_user)

    async def update_activity(self, user_id: int) -> None:
        """Обновляет время последней активности пользователя"""
        await self._uow.users.update_activity(user_id)
