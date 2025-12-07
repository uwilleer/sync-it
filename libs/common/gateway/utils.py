from common.gateway.config import gateway_config
from common.gateway.enums import ServiceEnum
from httpx import URL
from pydantic import HttpUrl


def build_service_url(service: ServiceEnum, path: str) -> URL:
    path = path.strip("/")

    pydantic_url = HttpUrl.build(
        scheme="http",
        host="api-gateway",
        port=gateway_config.port,
        path=f"{service}/{path}",
    )

    return URL(str(pydantic_url))
