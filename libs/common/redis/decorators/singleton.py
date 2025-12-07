from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from typing import ParamSpec, TypeVar

from common.logger import get_logger
from common.redis.config import redis_config
from common.redis.engine import get_sync_redis_client


logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def singleton(cache_ttl: int | timedelta) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    redis_client = get_sync_redis_client(redis_config.cache_dsn)

    def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            lock_name = f"lock:{func.__module__}.{func.__name__}"
            acquired = redis_client.set(lock_name, "locked", nx=True, ex=cache_ttl)

            if not acquired:
                logger.info("Function %s.%s is already running", func.__module__, func.__name__)
                return None

            try:
                return func(*args, **kwargs)
            finally:
                redis_client.delete(lock_name)

        return wrapper

    return decorator
