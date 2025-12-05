import asyncio
from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup
from common.logger import get_logger
from common.shared.clients import BaseClient
from common.shared.clients.head_hunter.config import head_hunter_config
from common.shared.clients.head_hunter.schemas import HeadHunterVacancyDetailResponse, HeadHunterVacancyListResponse
from common.shared.decorators.concurency import limit_requests
from httpx import URL, QueryParams, codes


logger = get_logger(__name__)


class HeadHunterClient(BaseClient):
    url = URL("https://api.hh.ru")
    ui_url = URL("https://hh.ru")

    vacancies_per_page = 100  # Количество вакансий на странице. Максимум 100
    vacancies_period = 1  # Количество дней, в пределах которых производится поиск по вакансиям

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._update_headers()

    async def get_newest_vacancies_ids(self, professions: Iterable[str]) -> list[int]:
        """Асинхронно получает id актуальных вакансиий."""
        logger.debug("Getting hh newest vacancies ids after %s")
        text_query = " OR ".join(professions)

        first_page_data = await self._fetch_page(page=0, text_query=text_query)
        all_vacancy_ids = [vacancy.id for vacancy in first_page_data.items]

        total_pages = first_page_data.pages
        if total_pages > 1:
            logger.debug("Fetching remaining %s pages...", total_pages - 1)

            tasks = [self._fetch_page(page=p, text_query=text_query) for p in range(1, total_pages)]
            for coro in asyncio.as_completed(tasks):
                page_data = await coro
                all_vacancy_ids.extend(vacancy.id for vacancy in page_data.items)

        logger.debug("Found %s hh new vacancies", len(all_vacancy_ids))

        return all_vacancy_ids

    # FIXME ограничить на уровне клиента, а не метода
    @limit_requests(20)
    async def get_vacancy_by_id(self, vacancy_id: int) -> HeadHunterVacancyDetailResponse | None:
        """Загружает и валидирует одну детальную вакансию по ее ID."""
        logger.debug("Getting hh vacancies by id %s", vacancy_id)
        detailed_url = f"{self.url}/vacancies/{vacancy_id}"
        response = await self.client.get(detailed_url)

        if response.status_code == codes.NOT_FOUND:
            return None

        response.raise_for_status()
        data = response.json()

        return HeadHunterVacancyDetailResponse.model_validate(data)

    # FIXME Узнать ограничение числа запросов
    @limit_requests(20)
    async def get_resume_text(self, resume_id: str) -> str | None:
        """Получает текст резюме по ID."""
        logger.debug("Getting hh resume by id %s", resume_id)

        resume_url = f"{self.ui_url}/resume/{resume_id}"
        response = await self.client.get(
            resume_url,
            headers={
                "Accept": "text/html",
            },
        )

        # Выдает 403, а не 404
        if response.status_code == codes.FORBIDDEN:
            return None

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        resume_wrapper = soup.select_one("div.resume-wrapper")

        return resume_wrapper.get_text(separator=" ")  # type: ignore[union-attr]

    def _update_headers(self) -> None:
        """Обновляет заголовки клиента для доступа к API HeadHunter. Позволяет увеличить RPS."""
        self.client.headers.update(
            {
                "Authorization": f"Bearer {head_hunter_config.access_token}",
                "User-Agent": f"{head_hunter_config.app_name} ({head_hunter_config.email})",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # Где-то нашел инфу, что ограничение на 30 запросов в секунду,
    # но стабильно работает только 5, иначе возникает 400 ошибка
    @limit_requests(5)
    async def _fetch_page(self, page: int, text_query: str) -> HeadHunterVacancyListResponse:
        """Загружает и валидирует одну страницу вакансий."""
        params = QueryParams(
            {
                "text": text_query,
                "per_page": self.vacancies_per_page,
                "period": self.vacancies_period,
                "page": page,
                "order_by": "publication_time",
            }
        )

        if len(str(params)) > 2000:  # noqa: PLR2004
            logger.warning("Possible long query")

        url = f"{self.url}/vacancies"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return HeadHunterVacancyListResponse.model_validate(data)


head_hunter_client = HeadHunterClient()
