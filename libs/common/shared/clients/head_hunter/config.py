from pydantic_settings import BaseSettings, SettingsConfigDict


class HeadHunterConfig(BaseSettings):
    client_id: str
    client_secret: str
    access_token: str
    email: str
    app_name: str

    model_config = SettingsConfigDict(env_prefix="SHARED_CLIENT_HEAD_HUNTER_")


head_hunter_config = HeadHunterConfig()
