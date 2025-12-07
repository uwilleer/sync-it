from collections.abc import Sequence

from common.shared.repositories import BaseRepository
from database.models import User, UserPreference
from database.models.enums import PreferencesCategoryCodeEnum
from sqlalchemy import delete, select


class UserPreferenceRepository(BaseRepository):
    async def get_by_user_id(self, user_id: int) -> Sequence[UserPreference]:
        """Находит предпочтения по пользователю."""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await self._session.execute(stmt)

        return result.scalars().all()

    async def filter_by_telegram_id_and_category(
        self, telegram_id: int, category_code: PreferencesCategoryCodeEnum
    ) -> Sequence[UserPreference]:
        """Находит предпочтения по пользователю и категории."""
        stmt = select(UserPreference).where(
            UserPreference.user.has(User.telegram_id == telegram_id),
            UserPreference.category_code == category_code,
        )

        result = await self._session.execute(stmt)

        return result.scalars().all()

    async def get_by_user_and_item(
        self, user_id: int, category_code: PreferencesCategoryCodeEnum, item_id: int
    ) -> UserPreference | None:
        """Находит предпочтение по пользователю, категории и ID опции."""
        stmt = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.category_code == category_code,
            UserPreference.item_id == item_id,
        )
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def add_bulk(self, preferences: list[UserPreference]) -> list[UserPreference]:
        """Добавляет несколько предпочтений за один запрос."""
        self._session.add_all(preferences)
        await self._session.flush()

        return preferences

    async def add(self, user_preference: UserPreference) -> UserPreference:
        """Добавляет новое предпочтение."""
        self._session.add(user_preference)
        await self._session.flush()
        await self._session.refresh(user_preference)

        return user_preference

    async def delete(self, user_preference: UserPreference) -> None:
        """Удаляет существующее предпочтение."""
        await self._session.delete(user_preference)
        await self._session.flush()

    async def delete_all_by_user_and_category(self, user_id: int, category_code: str) -> None:
        """Удаляет все предпочтения пользователя по категории."""
        stmt = delete(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.category_code == category_code,
        )
        await self._session.execute(stmt)
        await self._session.flush()
