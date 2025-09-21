from clients.schemas import SkillItemResponse, SkillListResponse, SkillSchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.redis.decorators import cache
from common.shared.clients import BaseClient
from common.shared.serializers.pickle import PickleSerializer
from httpx import codes


__all__ = ["skill_client"]


class _SkillClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/skills")

    # TODO: Возможен баг, когда в вакансии будет скилл, пользователь его захочет добавить,
    #  а кеш устарел, следовательно скилл не найдется.
    @cache(cache_ttl=60 * 60 * 24, serializer=PickleSerializer())
    async def get_all(self) -> list[SkillSchema]:
        response = await self.client.get(self.url)

        response.raise_for_status()
        response_model = SkillListResponse.model_validate(response.json())

        return response_model.skills

    async def get_by_name(self, name: str) -> SkillSchema | None:
        response = await self.client.get(f"{self.url}/{name}")
        if response.status_code == codes.NOT_FOUND:
            return None

        response.raise_for_status()
        response_model = SkillItemResponse.model_validate(response.json())

        return SkillSchema.model_validate(response_model.skill)

    async def extract_skills_from_text(self, text: str) -> list[SkillSchema]:
        """Извлекает скиллы из текста."""
        response = await self.client.post(f"{self.url}/extract", json={"text": text})
        response.raise_for_status()

        data = response.json()
        model_response = SkillListResponse.model_validate(data)

        return model_response.skills

    def configure_client(self) -> None:
        self.client.timeout = 15


skill_client = _SkillClient()
