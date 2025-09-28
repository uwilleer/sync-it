from dataclasses import dataclass

from async_lru import alru_cache
from clients.schemas import (
    SourceEnum,
    VacanciesSummaryResponse,
    VacanciesSummarySchema,
    VacancyWithNeighborsRequest,
    VacancyWithNeighborsResponse,
    VacancyWithNeighborsSchema,
)
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.redis.decorators.cache import cache
from common.shared.clients import BaseClient
from common.shared.serializers.pickle import PickleSerializer


__all__ = ["vacancy_client"]


# Костылище
@dataclass
class _SourceSchema:
    id: int
    name: str


class _VacancyClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PROCESSOR, "api/v1/vacancies")

    async def get_by_id_with_cursor_pagination(
        self,
        current_vacancy_id: int | None = None,
        professions: list[str] | None = None,
        grades: list[str] | None = None,
        work_formats: list[str] | None = None,
        skills: list[str] | None = None,
        sources: list[str] | None = None,
    ) -> VacancyWithNeighborsSchema:
        params_model = VacancyWithNeighborsRequest(
            current_vacancy_id=current_vacancy_id,
            professions=professions,
            grades=grades,
            work_formats=work_formats,
            skills=skills,
            sources=sources,
        )
        url = f"{self.url}/match"
        response = await self.client.get(
            url,
            params=params_model.model_dump(exclude_none=True),
        )
        data = response.json()
        model_response = VacancyWithNeighborsResponse.model_validate(data)

        return model_response.result

    @cache(cache_ttl=60 * 30, serializer=PickleSerializer())
    async def get_summary_vacancies(self) -> VacanciesSummarySchema:
        response = await self.client.get(f"{self.url}/summary")
        response.raise_for_status()

        data = response.json()
        model_response = VacanciesSummaryResponse.model_validate(data)

        return model_response.result

    @alru_cache(ttl=60 * 60 * 24)
    async def get_sources(self) -> list["_SourceSchema"]:  # noqa: PLR6301
        # FIXME За такое по рукам бить надо.
        sources = []

        for idx, source in enumerate(SourceEnum, start=1):
            sources.append(_SourceSchema(id=idx, name=source.humanize()))

        return sources


vacancy_client = _VacancyClient()
