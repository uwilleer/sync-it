import asyncio
from typing import Any

from clients.head_hunter.schemas import (
    HeadHunterVacancyDetailResponse,
    HeadHunterVacancyListResponse,
)
from clients.profession import profession_client
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.decorators.concurency import limit_requests
from core import service_config
from httpx import URL, QueryParams, codes


__all__ = ["head_hunter_client"]


logger = get_logger(__name__)


class _HeadHunterClient(BaseClient):
    url = URL("https://api.hh.ru/vacancies")

    vacancies_per_page = 100  # Количество вакансий на странице. Максимум 100
    vacancies_period = 1  # Количество дней, в пределах которых производится поиск по вакансиям

    # Последовательность id IT профессий согласно API HeadHunter
    # https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-professional-roles-dictionary
    professional_roles: tuple[int, ...] = ()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._update_headers()

    def _update_headers(self) -> None:
        """Обновляет заголовки клиента для доступа к API HeadHunter."""
        self.client.headers.update(
            {
                "Authorization": f"Bearer {service_config.hh_access_token}",
                "User-Agent": f"{service_config.hh_app_name} ({service_config.hh_email})",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # Где-то нашел инфу, что ограничение на 30 запросов в секунду,
    # но при постоянных долгих запросах выдается 403 как ddos.
    # Реальное долгосрочное ограничение 1 запрос в секунду.
    @limit_requests(10)
    async def _fetch_page(self, page: int, text_query: str) -> HeadHunterVacancyListResponse:
        """Загружает и валидирует одну страницу вакансий."""
        params = QueryParams(
            {
                "professional_role": self.professional_roles,
                "text": text_query,
                "per_page": self.vacancies_per_page,
                "period": self.vacancies_period,
                "page": page,
                "order_by": "publication_time",
            }
        )

        response = await self.client.get(self.url, params=params)
        response.raise_for_status()
        data = response.json()

        return HeadHunterVacancyListResponse.model_validate(data)

    async def get_newest_vacancy_ids(self) -> list[int]:
        """Асинхронно получает id актуальных вакансиий."""
        professions = await profession_client.get_all()
        text_query = " OR ".join([p.name for p in professions])

        first_page_data = await self._fetch_page(page=0, text_query=text_query)
        all_vacancy_ids = [vacancy.id for vacancy in first_page_data.items]

        total_pages = first_page_data.pages
        if total_pages > 1:
            logger.debug("Fetching remaining %s pages...", total_pages - 1)

            tasks = [self._fetch_page(page=p, text_query=text_query) for p in range(1, total_pages)]
            for coro in asyncio.as_completed(tasks):
                page_data = await coro
                all_vacancy_ids.extend(vacancy.id for vacancy in page_data.items)

        return all_vacancy_ids

    async def get_vacancy_by_id(self, vacancy_id: int) -> HeadHunterVacancyDetailResponse | None:
        """Загружает и валидирует одну детальную вакансию по ее ID."""
        detailed_url = f"{self.url}/{vacancy_id}"
        response = await self.client.get(detailed_url)

        if response.status_code == codes.NOT_FOUND:
            return None

        response.raise_for_status()
        data = response.json()

        return HeadHunterVacancyDetailResponse.model_validate(data)


head_hunter_client = _HeadHunterClient()
