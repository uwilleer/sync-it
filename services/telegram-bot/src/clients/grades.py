from async_lru import alru_cache
from clients.schemas import GradeListResponse, GradeSchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


__all__ = ["grade_client"]


class _GradeClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/grades")

    @alru_cache(ttl=60 * 60 * 24)
    async def get_all(self) -> list[GradeSchema]:
        response = await self.client.get(self.url)
        data = response.json()
        model_response = GradeListResponse.model_validate(data)

        return model_response.grades


grade_client = _GradeClient()
