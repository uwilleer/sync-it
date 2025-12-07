from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from common.logger import get_logger
from common.redis.config import redis_config
from common.redis.engine import get_async_redis_client
from common.shared.serializers import AbstractSerializer, JSONSerializer
from redis.asyncio import Redis


logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def build_key(*args: Any, **kwargs: Any) -> str:
    """Создает ключ для кеширования в Redis."""
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(f"{key}={value}" for key, value in sorted(kwargs.items()))

    return f"{args_str}:{kwargs_str}"


def get_key_prefix(fn: Callable[..., Any]) -> str:
    """Создает префикс для кешируемого ключа."""
    return f"{fn.__module__}:{fn.__name__}"


async def set_redis_value(
    redis_instance: Redis,
    key: bytes | str,
    value: bytes,
    cache_ttl: int | None = None,
    *,
    is_transaction: bool = False,
) -> None:
    """Кеширует значение по ключу в Redis."""
    async with redis_instance.pipeline(transaction=is_transaction) as pipeline:
        await pipeline.set(key, value)
        logger.debug("Set cache. key=%s, value=%s", key, value)
        if cache_ttl:
            await pipeline.expire(key, cache_ttl)
        await pipeline.execute()


def cache(
    cache_ttl: int,
    key_builder: Callable[..., str] = build_key,
    serializer: AbstractSerializer | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Кеширует результат функции на основе аргументов функции"""
    serializer = serializer or JSONSerializer()

    def decorator(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            redis_client = get_async_redis_client(redis_config.cache_dsn)

            key_build = key_builder(*args, **kwargs)
            key_prefix = get_key_prefix(fn)
            key = f"{key_prefix}:{key_build}"

            cached_value = await redis_client.get(key)
            if cached_value is not None:
                logger.debug("Getting cache. key=%s", key)
                return cast("R", serializer.deserialize(cached_value))

            result = await fn(*args, **kwargs)

            await set_redis_value(
                redis_client,
                key,
                serializer.serialize(result),
                cache_ttl,
            )

            return result

        return wrapper

    return decorator
