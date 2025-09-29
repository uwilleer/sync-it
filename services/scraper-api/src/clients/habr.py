from datetime import datetime

from clients.base import BaseParserClient
from clients.schemas import HabrVacancyListResponse, PingResponse
from common.logger import get_logger
from httpx import URL, QueryParams
from parsers import HabrParser
from schemas import HabrDetailedVacancySchema


__all__ = ["habr_client"]


logger = get_logger(__name__)


class _HabrClient(BaseParserClient):
    url = URL("https://career.habr.com/vacancies")
    _api_url = URL("https://career.habr.com/api/frontend/vacancies")
    parser = HabrParser

    async def ping(self) -> PingResponse:
        response = await self.client.get(self.url)
        response.raise_for_status()

        return PingResponse()

    async def get_vacancy_by_id(self, vacancy_id: int) -> HabrDetailedVacancySchema:
        detailed_url = f"{self.url}/{vacancy_id}"
        response = await self.client.get(detailed_url)

        response.raise_for_status()

        return self.parser.parse_detailed_vacancy(response.text, vacancy_id)

    async def get_newest_vacancies_ids(self, date_gte: datetime) -> list[int]:
        newest_vacancy_ids: list[int] = []

        logger.info("Getting newest vacancies ids after %s", date_gte)

        first_page = await self._fetch_vacancies(page=1)
        logger.debug("Total pages: %s", first_page.meta.total_pages)

        current_page = 1
        continue_pagination = True

        while continue_pagination and current_page <= first_page.meta.total_pages:
            vacancies_response = await self._fetch_vacancies(page=current_page)
            for vacancy in vacancies_response.list:
                if vacancy.published_date.date < date_gte:
                    logger.debug("Found old vacancy. Break.")
                    continue_pagination = False
                    break

                newest_vacancy_ids.append(vacancy.id)
            current_page += 1

        return sorted(newest_vacancy_ids, reverse=True)

    async def _fetch_vacancies(self, page: int = 1) -> HabrVacancyListResponse:
        params = QueryParams({"sort": "date", "type": "all", "page": page})
        response = await self.client.get(self._api_url, params=params)
        response.raise_for_status()
        data = response.json()

        return HabrVacancyListResponse.model_validate(data)


habr_client = _HabrClient()
