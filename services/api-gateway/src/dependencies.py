from typing import Annotated

from common.environment.config import env_config
from common.gateway.config import gateway_config
from common.logger import get_logger
from fastapi import Header, HTTPException
from starlette import status
from starlette.requests import Request


__all__ = ["validate_api_key"]

logger = get_logger(__name__)


async def validate_api_key(request: Request, x_api_key: Annotated[str | None, Header()] = None) -> None:  # noqa: RUF029
    """
    Проверяет доступ к API Gateway.

    - Пропускает запросы в dev-mode.
    - Для всех остальных запросов требует валидный X-API-Key.
    """
    if env_config.debug:
        logger.info("Debug mode, skipping API key check")
        return

    if request.client is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not determine client IP address")

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    if x_api_key == gateway_config.api_key:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key",
    )
