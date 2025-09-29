import asyncio
from typing import TYPE_CHECKING

from clients import habr_client
from common.logger import get_logger
from common.shared.schemas import HttpsUrl
from database.models.enums import SourceEnum
from parsers.base import BaseParser
from schemas.vacancies import HabrVacancyCreate
from utils import generate_fingerprint, generate_vacancy_hash


if TYPE_CHECKING:
    from services import HabrVacancyService

__all__ = ["HabrParser"]


logger = get_logger(__name__)


class HabrParser(BaseParser["HabrVacancyService"]):
    service: "HabrVacancyService"

    async def parse(self) -> None:
        logger.info("Starting Habr parser")

        last_vacancy = await self.service.get_last_vacancy()
        last_vacancy_date = last_vacancy.published_at if last_vacancy else None
        newest_vacancy_ids = await habr_client.get_newest_vacancies_ids(last_vacancy_date)
        logger.debug("Found %s actual vacancies", len(newest_vacancy_ids))
        vacancy_hashes = [generate_vacancy_hash(v_id, SourceEnum.HABR) for v_id in newest_vacancy_ids]
        existing_hashes = await self.service.get_existing_hashes(vacancy_hashes)
        new_vacancies_ids = [
            v_id for v_id in newest_vacancy_ids if generate_vacancy_hash(v_id, SourceEnum.HABR) not in existing_hashes
        ]

        logger.debug("Found %s new vacancies", len(new_vacancies_ids))

        tasks = [habr_client.get_vacancy_by_id(vacancy_id) for vacancy_id in new_vacancies_ids]

        for coro in asyncio.as_completed(tasks):
            try:
                vacancy_detail = await coro
            except Exception as e:
                logger.exception("Error processing vacancy", exc_info=e)
                continue

            if not vacancy_detail:
                logger.debug("Skipping not founded vacancy")
                continue

            fingerprint = generate_fingerprint(vacancy_detail.text)
            duplicate_hash = await self.service.find_duplicate_vacancy_by_fingerprint(fingerprint)
            if duplicate_hash:
                logger.debug(
                    "Found duplicate vacancy. New vacancy id: %s",
                    vacancy_detail.id,
                )
                await self.service.update_vacancy_published_at(duplicate_hash, vacancy_detail.datetime)
                continue

            vacancy_create = HabrVacancyCreate(
                fingerprint=fingerprint,
                link=HttpsUrl(f"https://career.habr.com/vacancies/{vacancy_detail.id}"),
                external_id=vacancy_detail.id,
                published_at=vacancy_detail.datetime,
                data=vacancy_detail.text,
            )
            await self.service.add_vacancy(vacancy_create, with_refresh=False)
            logger.debug("Added vacancy %s", vacancy_create.link)
