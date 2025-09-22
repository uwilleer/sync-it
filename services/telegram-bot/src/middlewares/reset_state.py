from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from commands import BotCommandEnum
from common.logger import get_logger


__all__ = ["ResetStateMiddleware"]


if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


logger = get_logger(__name__)


def _is_command(text: str | None) -> bool:
    if not text:
        return False
    return text.strip()[1:] in BotCommandEnum


class ResetStateMiddleware(BaseMiddleware):
    """Очищает state если пользователь отправил команду (/start, /faq, ...)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        state: FSMContext = data["state"]

        if _is_command(event.text):
            logger.debug("State cleared")
            await state.clear()

        return await handler(event, data)
