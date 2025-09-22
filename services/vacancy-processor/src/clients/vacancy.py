from clients.schemas import VacancyProcessedResponse, VacancyResponse, VacancySchema
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests


__all__ = ["vacancy_client"]


logger = get_logger(__name__)


class _VacancyClient(BaseClient):
    url = build_service_url(ServiceEnum.VACANCY_PARSER, "/api/v1/vacancies")

    @limit_requests(30)
    async def get_vacancies(self) -> list[VacancySchema]:
        response = await self.client.get(self.url)
        response.raise_for_status()

        data = response.json()
        model_response = VacancyResponse(**data)

        return model_response.vacancies

    @limit_requests(10)
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

    def configure_client(self) -> None:
        self.client.timeout = 30


vacancy_client = _VacancyClient()
