from clients.schemas import SkillListResponse, SkillSchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


__all__ = ["skill_client"]


class _SkillClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/skills")

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
