import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
import time
from typing import ParamSpec, TypeVar

from common.logger import get_logger


logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def limit_requests(limit: int = 1) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Декоратор для ограничения параллельного выполнения и частоты вызовов
    асинхронной функции.

    :param limit: Максимальное количество одновременных выполнений.
    """
    delay = 1 / limit

    semaphore = asyncio.Semaphore(limit)
    lock = asyncio.Lock()
    last_start_time = 0.0

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal last_start_time

            async with semaphore:
                async with lock:
                    current_time = time.monotonic()
                    next_allowed_start = last_start_time + delay
                    this_task_start_time = max(current_time, next_allowed_start)

                    sleep_duration = this_task_start_time - current_time
                    last_start_time = this_task_start_time

                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

                return await func(*args, **kwargs)

        return wrapper

    return decorator
