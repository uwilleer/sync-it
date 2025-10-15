import logging

from common.environment.config import env_config
from common.logger import get_logger
from common.sentry.config import sentry_config
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


__all__ = ["init_sentry"]

logger = get_logger(__name__)


def init_sentry() -> None:
    if not sentry_config.enabled:
        logger.info("Skip initializing Sentry")
        return

    logger.info("Initializing Sentry")

    sentry_sdk.init(
        dsn=str(sentry_config.dsn_url),
        integrations=[LoggingIntegration(event_level=logging.WARNING), CeleryIntegration()],
        environment=env_config.mode,
        traces_sample_rate=sentry_config.traces_sample_rate,
        profile_lifecycle=sentry_config.profile_lifecycle.value,
    )
