from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from cachetools import TTLCache
from common.logger import get_logger
from core import service_config


logger = get_logger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """Ограничивает количество запросов от одного пользователя."""

    _cache: TTLCache[int, Any]

    def __init__(self, rate_limit: float = service_config.rate_limit) -> None:
        self._cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        user_id = user.id
        if user_id in self._cache:
            await event.answer("Пожалуйста, не так быстро.", show_alert=False)
            return None

        self._cache[user_id] = None
        return await handler(event, data)
