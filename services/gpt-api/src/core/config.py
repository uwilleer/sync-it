from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    gemini_api_key: SecretStr

    model_config = SettingsConfigDict(env_prefix="GPT_API_")


service_config = ServiceConfig()
