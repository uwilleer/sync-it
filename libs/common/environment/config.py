from common.environment.enums import EnvironmentEnum
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    mode: EnvironmentEnum = EnvironmentEnum.production
    service_internal_host: str = "0.0.0.0"
    service_internal_port: int = Field(default=8000, ge=1, le=65535)

    model_config = SettingsConfigDict(env_prefix="ENV_")

    @property
    def debug(self) -> bool:
        return EnvironmentEnum.development == self.mode


env_config = EnvConfig()
