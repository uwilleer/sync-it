from pydantic import BaseModel

from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.shared.clients import BaseClient


__all__ = ["matcher_client"]


class _MatchRequest(BaseModel):
    professions: list[str]
    grades: list[str]
    work_formats: list[str]
    skills: list[str]
    sources: list[str]


class _MatchResponse(BaseModel):
    vacancy_ids: list[int]


class _MatcherClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_MATCHER, "/api/v1/match")

    async def match(self, *, professions: list[str], grades: list[str], work_formats: list[str], skills: list[str], sources: list[str]) -> list[int]:
        body = _MatchRequest(
            professions=professions,
            grades=grades,
            work_formats=work_formats,
            skills=skills,
            sources=sources,
        )
        response = await self.client.post(str(self.url), json=body.model_dump())
        response.raise_for_status()
        data = response.json()
        parsed = _MatchResponse.model_validate(data)
        return parsed.vacancy_ids


matcher_client = _MatcherClient()

