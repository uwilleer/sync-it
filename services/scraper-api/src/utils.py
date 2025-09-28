from common.logger import get_logger
from httpx import Response, codes


__all__ = ["validate_health_response"]


logger = get_logger(__name__)


def validate_health_response(response: Response) -> None:
    if response.status_code != codes.OK or "Telegram News – Telegram" not in response.text:
        logger.error("Unexpected healthcheck response: %s", response.text)
        raise ValueError("Unexpected healthcheck response")
