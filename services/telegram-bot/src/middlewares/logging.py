from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from common.logger import get_logger


if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        logger.debug(event.model_dump_json(indent=4, exclude_none=True, exclude_defaults=True))

        fsm_context: FSMContext | None = data["state"]
        if fsm_context:
            current_state = await fsm_context.get_state()
            if current_state:
                logger.debug("FSM State: %s", current_state)

        return await handler(event, data)
