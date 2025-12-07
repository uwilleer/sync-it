from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services import UserPreferenceService, UserService


class ServiceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        uow = data["uow"]

        data["user_service"] = UserService(uow)
        data["user_preferences_service"] = UserPreferenceService(uow)

        return await handler(event, data)
