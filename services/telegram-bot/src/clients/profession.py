from async_lru import alru_cache
from clients.schemas import ProfessionListResponse, ProfessionSchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


__all__ = ["profession_client"]


class _ProfessionClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/professions")

    @alru_cache(ttl=60 * 60 * 24)
    async def get_all(self) -> list[ProfessionSchema]:
        response = await self.client.get(self.url)
        data = response.json()
        model_response = ProfessionListResponse.model_validate(data)

        return model_response.professions


profession_client = _ProfessionClient()
