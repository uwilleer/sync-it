from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    telethon_api_id: int
    telethon_api_hash: str
    telethon_session_string: str
    proxy: str | None = None

    model_config = SettingsConfigDict(env_prefix="SCRAPER_API_")


service_config = ServiceConfig()
