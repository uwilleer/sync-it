from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    model_config = SettingsConfigDict(env_prefix="GPT_API_")


service_config = ServiceConfig()
