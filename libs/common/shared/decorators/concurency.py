import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
import time
from typing import ParamSpec, TypeVar
from weakref import WeakKeyDictionary

from common.logger import get_logger


logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def limit_requests(limit: int = 1) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Декоратор для ограничения параллельного выполнения и частоты вызовов
    асинхронной функции.

    :param limit: Максимальное количество одновременных выполнений.
    """
    delay = 1 / limit

    # Храним Semaphore и Lock для каждого event loop отдельно
    semaphores: WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Semaphore] = WeakKeyDictionary()
    locks: WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = WeakKeyDictionary()
    last_start_times: dict[asyncio.AbstractEventLoop, float] = {}

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Получаем текущий event loop
            loop = asyncio.get_running_loop()

            # Создаем или получаем Semaphore и Lock для текущего event loop
            if loop not in semaphores:
                semaphores[loop] = asyncio.Semaphore(limit)
                locks[loop] = asyncio.Lock()
                last_start_times[loop] = 0.0

            semaphore = semaphores[loop]
            lock = locks[loop]
            last_start_time = last_start_times[loop]

            async with semaphore:
                async with lock:
                    current_time = time.monotonic()
                    next_allowed_start = last_start_time + delay
                    this_task_start_time = max(current_time, next_allowed_start)

                    sleep_duration = this_task_start_time - current_time
                    last_start_times[loop] = this_task_start_time

                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

                return await func(*args, **kwargs)

        return wrapper

    return decorator
