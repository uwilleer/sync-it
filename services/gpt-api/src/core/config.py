from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    openai_api_key: SecretStr
    openai_proxy: str | None = None
    openai_model: str = "gpt-5-nano"

    model_config = SettingsConfigDict(env_prefix="GPT_API_")


service_config = ServiceConfig()
