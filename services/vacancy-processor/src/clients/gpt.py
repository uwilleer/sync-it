from clients.schemas import CompletionResponse
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests


__all__ = ["gpt_client"]


class _GPTClient(BaseClient):
    url = build_service_url(ServiceEnum.GPT_API, "/api/v1/completion")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 30

    @limit_requests(500)
    async def get_completion(self, prompt: str) -> str:
        response = await self.client.post(self.url, json={"prompt": prompt})
        response.raise_for_status()

        data = CompletionResponse(**response.json())

        return data.message


gpt_client = _GPTClient()
