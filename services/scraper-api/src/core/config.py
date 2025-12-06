from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    telethon_session_name: str
    telethon_api_id: int
    telethon_api_hash: str

    model_config = SettingsConfigDict(env_prefix="SCRAPER_API_")


service_config = ServiceConfig()
