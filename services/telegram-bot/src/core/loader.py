from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from common.redis.config import redis_config
from common.redis.engine import get_async_redis_client
from core import service_config


storage = RedisStorage(
    redis=get_async_redis_client(redis_config.bot_bot_dsn),
    key_builder=DefaultKeyBuilder(with_bot_id=True),
    state_ttl=service_config.state_ttl,
    data_ttl=service_config.data_ttl,
)

bot = Bot(token=service_config.token)
dp = Dispatcher(storage=storage)
