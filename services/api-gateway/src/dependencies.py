from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from typing import Annotated

from common.environment.config import env_config
from common.gateway.config import gateway_config
from common.logger import get_logger
from fastapi import Header, HTTPException
from starlette import status
from starlette.requests import Request


__all__ = ["validate_api_key"]

logger = get_logger(__name__)


# Определено в compose файле
TRUSTED_NETWORKS: set[IPv4Network | IPv6Network] = {
    ip_network("172.25.0.0/16"),
}


async def validate_api_key(request: Request, x_api_key: Annotated[str | None, Header()] = None) -> None:  # noqa: RUF029
    """
    Проверяет доступ к API Gateway.

    - Пропускает запросы в dev-mode.
    - Пропускает запросы на вебхук Telegram без проверки ключа.
    - Для всех остальных запросов требует валидный X-API-Key.
    """
    if env_config.debug:
        logger.info("Debug mode, skipping API key check")
        return

    if request.url.path.startswith("/telegram-bot/webhook"):
        return

    if request.client is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not determine client IP address")

    client_ip = ip_address(request.client.host)
    if any(client_ip in network for network in TRUSTED_NETWORKS):
        return

    if x_api_key == gateway_config.api_key:
        return

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key",
    )
