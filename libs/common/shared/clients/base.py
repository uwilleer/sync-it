from common.gateway.config import gateway_config
from common.shared.clients.http import http_client
from httpx import URL, AsyncClient


__all__ = ["BaseClient"]


class BaseClient:
    url: URL

    def __init__(self, client: AsyncClient = http_client) -> None:
        self.client = client
        self.configure_client()

    def configure_client(self) -> None:
        """Конфигурирует клиент перед работой"""
        self.client.headers.update({"x-api-key": gateway_config.api_key})
        self.client.timeout = 60
