from aiogram import Dispatcher
from common.environment.config import env_config
from common.logger import get_logger
from middlewares.answer_callback import AnswerCallbackMiddleware
from middlewares.auth import AuthMiddleware
from middlewares.database import DatabaseMiddleware
from middlewares.logging import LoggingMiddleware
from middlewares.reset_state import ResetStateMiddleware
from middlewares.service import ServiceMiddleware
from middlewares.throttling import ThrottlingMiddleware


__all__ = ["register_middlewares"]


logger = get_logger(__name__)


def register_middlewares(dp: Dispatcher) -> None:
    logger.info("Registering middlewares")

    if env_config.debug:
        dp.update.outer_middleware(LoggingMiddleware())

    dp.message.outer_middleware(ThrottlingMiddleware())
    dp.callback_query.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())
    dp.update.outer_middleware(ServiceMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(ResetStateMiddleware())

    dp.callback_query.middleware(AnswerCallbackMiddleware())
