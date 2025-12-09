"""Утилиты для работы с асинхронным кодом."""

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

from common.logger import get_logger


__all__ = ["run_async"]


logger = get_logger(__name__)

T = TypeVar("T")


def run_async[T](coro: Awaitable[T]) -> T:
    """
    Правильно запускает async функцию в синхронном контексте (например, в Celery задачах).

    Создает новый изолированный event loop для выполнения async кода,
    что безопасно для использования в Celery задачах.

    Args:
        coro: Awaitable объект (coroutine) для выполнения

    Returns:
        Результат выполнения coroutine

    Example:
        ```python
        @app.task
        def my_task():
            run_async(async_function())
        ```
    """

    def _check_running_loop() -> None:
        """Проверяет, не запущен ли уже event loop, и выбрасывает ошибку если запущен."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # RuntimeError означает, что нет запущенного event loop
            # Это нормальная ситуация для Celery задач
            return
        # Если мы здесь, значит loop уже запущен - это ошибка
        raise RuntimeError("run_async() cannot be called from a running event loop. Use await directly instead.")

    # Проверяем, не запущен ли уже event loop
    _check_running_loop()

    # Создаем новый изолированный event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        # Закрываем loop и очищаем
        try:
            # Отменяем все оставшиеся задачи
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            # Ждем завершения отмененных задач
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except (RuntimeError, asyncio.CancelledError, GeneratorExit) as e:
            # Ловим конкретные исключения, которые могут возникнуть при очистке
            logger.warning("Error cleaning up event loop tasks: %s", e, exc_info=e)
        finally:
            loop.close()
            asyncio.set_event_loop(None)
