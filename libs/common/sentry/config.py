from common.sentry.enums import ProfileLifecycleEnum
from common.shared.schemas.http import HttpsUrl
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SentryConfig(BaseSettings):
    enabled: bool = False
    dsn_url: HttpsUrl | None = None
    traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    profiles_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    profile_lifecycle: ProfileLifecycleEnum = ProfileLifecycleEnum.TRACE
    slow_sql_threshold: float = Field(default=1.0, gt=0.0)

    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    @property
    def slow_api_threshold(self) -> float:
        return self.slow_sql_threshold


sentry_config = SentryConfig()
