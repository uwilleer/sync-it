from clients.schemas import VacanciesListRequest, VacancyListResponse, VacancyProcessedResponse, VacancySchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests


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

    @limit_requests(16)
    async def delete(self, vacancy: VacancySchema) -> bool:
        detail_vacancy_url = f"{self.url}/{vacancy.hash}"

        response = await self.client.post(detail_vacancy_url)
        response.raise_for_status()

        data = response.json()
        model_response = VacancyProcessedResponse(**data)

        if not model_response.is_processed:
            logger.error("Failed to mark vacancy as processed: %s", vacancy.link)
            return False

        return True


vacancy_client = _VacancyClient()
