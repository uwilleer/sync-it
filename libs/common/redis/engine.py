from functools import lru_cache
from typing import cast

from pydantic import RedisDsn
from redis import Redis
from redis.asyncio import Redis as AsyncRedis


@lru_cache
def get_async_redis_client(dsn: RedisDsn) -> AsyncRedis:
    return cast("AsyncRedis", AsyncRedis.from_url(str(dsn)))


@lru_cache
def get_sync_redis_client(dsn: RedisDsn) -> Redis:
    return Redis.from_url(str(dsn))
