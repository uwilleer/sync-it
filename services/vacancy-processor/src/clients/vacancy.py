from clients.schemas import (
    VacanciesListRequest,
    VacancyListResponse,
    VacancyProcessedBody,
    VacancyProcessedResponse,
    VacancySchema,
)
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient


__all__ = ["vacancy_client"]


logger = get_logger(__name__)


class _VacancyClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PARSER, "/api/v1/vacancies")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 30

    async def get_vacancies(self) -> list[VacancySchema]:
        params = VacanciesListRequest(limit=300)
        response = await self.client.get(self.url, params=params.model_dump())
        response.raise_for_status()

        data = response.json()
        model_response = VacancyListResponse(**data)

        logger.info("Received %d vacancies from vacancy parser", len(model_response.vacancies))

        return model_response.vacancies

    async def mark_as_processed_bulk(self, hashes: list[str]) -> int:
        url = f"{self.url}/mark-processed"

        body = VacancyProcessedBody(hashes=hashes)
        response = await self.client.post(url, json=body.model_dump())
        response.raise_for_status()

        data = response.json()
        model_response = VacancyProcessedResponse(**data)

        return model_response.updated_count


vacancy_client = _VacancyClient()
