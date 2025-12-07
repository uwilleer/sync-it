from async_lru import alru_cache
from clients.schemas import WorkFormatResponse, WorkFormatSchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


class _WorkFormatClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/work_formats")

    @alru_cache(ttl=60 * 60 * 24)
    async def get_all(self) -> list[WorkFormatSchema]:
        response = await self.client.get(self.url)
        data = response.json()
        model_response = WorkFormatResponse.model_validate(data)

        return model_response.work_formats


work_format_client = _WorkFormatClient()
