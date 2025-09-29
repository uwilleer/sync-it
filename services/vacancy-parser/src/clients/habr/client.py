from datetime import datetime

from clients.habr.schemas import (
    HabrVacanciesDetailedResponse,
    HabrVacanciesListResponse,
    HabrVacanciesRequest,
    HabrVacancySchema,
)
from common.gateway.enums import ServiceEnum
from common.gateway.utils import build_service_url
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests
from httpx import codes


__all__ = ["habr_client"]


logger = get_logger(__name__)


class _HabrClient(BaseClient):
    url = build_service_url(ServiceEnum.SCRAPER_API, "/api/v1/habr/vacancies")

    def configure_client(self) -> None:
        super().configure_client()
        self.client.timeout = 30

    async def get_newest_vacancies_ids(self, date_gte: datetime | None) -> list[int]:
        logger.debug("Getting habr newest vacancies ids after %s", date_gte)
        params = HabrVacanciesRequest(date_gte=date_gte)

        timeout = 360 if date_gte else self.client.timeout
        response = await self.client.get(self.url, params=params.model_dump(exclude_none=True), timeout=timeout)
        response.raise_for_status()

        data = response.json()
        model_response = HabrVacanciesListResponse.model_validate(data)

        return model_response.vacancies

    @limit_requests(10)
    async def get_vacancy_by_id(self, vacancy_id: int) -> HabrVacancySchema | None:
        logger.debug("Getting habr vacancies by id %s", vacancy_id)
        url = f"{self.url}/{vacancy_id}"

        response = await self.client.get(url)

        if response.status_code == codes.NOT_FOUND:
            return None

        response.raise_for_status()
        data = response.json()

        model_response = HabrVacanciesDetailedResponse.model_validate(data)

        return model_response.vacancy


habr_client = _HabrClient()
