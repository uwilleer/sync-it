from common.shared.schemas.http import HttpsUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    db_schema: str = "telegram_bot"

    token: str
    support_username: str
    rate_limit: float  # for throttling control in seconds
    use_webhook: bool
    webhook_url: HttpsUrl
    webhook_api_key: str

    state_ttl: int
    data_ttl: int

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_BOT_")


service_config = ServiceConfig()
