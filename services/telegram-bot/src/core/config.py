from common.shared.schemas.http import HttpsUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    db_schema: str = "telegram_bot"

    token: str
    support_username: str
    rate_limit: float = 0.5  # throttling control in seconds
    use_webhook: bool = False
    webhook_url: HttpsUrl | None = None
    webhook_api_key: str | None = None

    state_ttl: int = 600  # 10 minutes
    data_ttl: int = 86400  # 1 day

    proxy: str | None = None

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_BOT_")


service_config = ServiceConfig()
