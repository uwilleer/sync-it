from common.sentry.enums import ProfileLifecycleEnum
from common.shared.schemas.http import HttpsUrl
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SentryConfig(BaseSettings):
    enabled: bool
    dsn_url: HttpsUrl
    traces_sample_rate: float = Field(ge=0.0, le=1.0)
    profiles_sample_rate: float = Field(ge=0.0, le=1.0)
    profile_lifecycle: ProfileLifecycleEnum
    slow_sql_threshold: float = Field(gt=0.0)

    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    @property
    def slow_api_threshold(self) -> float:
        return self.slow_sql_threshold


sentry_config = SentryConfig()
