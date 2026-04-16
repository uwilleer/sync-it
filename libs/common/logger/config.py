from common.logger.enums import LogLevelEnum
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    level: LogLevelEnum

    model_config = SettingsConfigDict(env_prefix="LOG_")


log_config = LogConfig()
