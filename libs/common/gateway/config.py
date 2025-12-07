from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewayConfig(BaseSettings):
    host: str
    port: int = Field(ge=1, le=65535)
    api_key: str

    model_config = SettingsConfigDict(env_prefix="API_GATEWAY_")


gateway_config = GatewayConfig()
