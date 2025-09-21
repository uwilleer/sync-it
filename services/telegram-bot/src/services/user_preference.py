from collections.abc import Iterable

from common.logger import get_logger
from common.shared.services import BaseUOWService
from database.models import UserPreference
from database.models.enums import PreferencesCategoryCodeEnum
from schemas.user_preference import UserPreferenceCreate, UserPreferenceRead
from unitofwork import UnitOfWork


__all__ = ["UserPreferenceService"]


logger = get_logger(__name__)


class UserPreferenceService(BaseUOWService[UnitOfWork]):
    async def get_by_user_id(self, user_id: int) -> list[UserPreferenceRead]:
        preferences = await self._uow.user_preferences.get_by_user_id(user_id)

        return [UserPreferenceRead.model_validate(p) for p in preferences]

    async def filter_by_telegram_id_and_category(
        self, telegram_id: int, code: PreferencesCategoryCodeEnum
    ) -> list[UserPreferenceRead]:
        preferences = await self._uow.user_preferences.filter_by_telegram_id_and_category(telegram_id, code)

        return [UserPreferenceRead.model_validate(p) for p in preferences]

    async def replace_user_preferences(
        self,
        user_id: int,
        category_code: PreferencesCategoryCodeEnum,
        preferences: Iterable[UserPreferenceCreate],
    ) -> list[UserPreference]:
        """Полностью заменяет предпочтения пользователя по категории."""
        await self._uow.user_preferences.delete_all_by_user_and_category(user_id, category_code)

        new_preferences = [
            UserPreference(
                user_id=pref.user_id,
                category_code=pref.category_code,
                item_id=pref.item_id,
                item_name=pref.item_name,
            )
            for pref in preferences
        ]

        return await self._uow.user_preferences.add_bulk(new_preferences)

    async def toggle_preference(self, user_preference: UserPreferenceCreate) -> bool:
        """
        Переключает состояние предпочтения для пользователя.

        Если предпочтение было - удаляет его.
        Если не было - добавляет.

        Возвращает True, если предпочтение было добавлено, False — если удалено.
        """
        logger.debug(
            "Toggle preference for user id %s, category code: %s, item id: %s",
            user_preference.user_id,
            user_preference.category_code,
            user_preference.item_id,
        )

        existing_preference = await self._uow.user_preferences.get_by_user_and_item(
            user_id=user_preference.user_id,
            category_code=user_preference.category_code,
            item_id=user_preference.item_id,
        )

        if existing_preference:
            await self._uow.user_preferences.delete(existing_preference)
            return False

        new_preference = UserPreference(
            user_id=user_preference.user_id,
            category_code=user_preference.category_code,
            item_id=user_preference.item_id,
            item_name=user_preference.item_name,
        )
        await self._uow.user_preferences.add(new_preference)

        return True
