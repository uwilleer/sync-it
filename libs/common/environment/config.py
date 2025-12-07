from common.environment.enums import EnvironmentEnum
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    mode: EnvironmentEnum
    service_internal_host: str
    service_internal_port: int = Field(ge=1, le=65535)

    model_config = SettingsConfigDict(env_prefix="ENV_")

    @property
    def debug(self) -> bool:
        return EnvironmentEnum.development == self.mode


env_config = EnvConfig()
