import asyncio
from typing import TYPE_CHECKING

from clients import head_hunter_client
from common.logger import get_logger
from common.shared.schemas import HttpsUrl
from database.models.enums import SourceEnum
from parsers.base import BaseParser
from schemas.vacancies import HeadHunterVacancyCreate
from unitofwork import UnitOfWork
from utils import clear_html, generate_fingerprint, generate_vacancy_hash


if TYPE_CHECKING:
    from clients.head_hunter.schemas import HeadHunterVacancyDetailResponse

    from services import HeadHunterVacancyService


__all__ = ["HeadHunterParser"]


logger = get_logger(__name__)


class HeadHunterParser(BaseParser["HeadHunterVacancyService", "HeadHunterVacancyCreate"]):
    def __init__(self, uow: UnitOfWork, service: "HeadHunterVacancyService") -> None:
        super().__init__(uow, service)
        self.service = service

    async def parse(self) -> None:
        logger.info("Starting HeadHunter parser")

        newest_vacancy_ids = await head_hunter_client.get_newest_vacancies_ids()
        vacancy_hashes = [generate_vacancy_hash(v_id, SourceEnum.HEAD_HUNTER) for v_id in newest_vacancy_ids]
        existing_hashes = await self.service.get_existing_hashes(vacancy_hashes)
        new_vacancies_ids = {
            v_id
            for v_id in newest_vacancy_ids
            if generate_vacancy_hash(v_id, SourceEnum.HEAD_HUNTER) not in existing_hashes
        }

        logger.debug("Found %s new vacancies", len(new_vacancies_ids))

        tasks = [head_hunter_client.get_vacancy_by_id(vacancy_id) for vacancy_id in new_vacancies_ids]
        vacancy_details: list[HeadHunterVacancyDetailResponse | BaseException | None] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        for vacancy_detail in vacancy_details:
            if isinstance(vacancy_detail, BaseException):
                logger.error("Error fetching vacancy", exc_info=vacancy_detail)
                continue
            if not vacancy_detail:
                continue

            vacancy_description = clear_html(vacancy_detail.description)

            fingerprint = generate_fingerprint(vacancy_description)
            duplicate_hash = await self.service.find_duplicate_vacancy_by_fingerprint(fingerprint)
            if duplicate_hash:
                logger.debug(
                    "Found duplicate vacancy. New vacancy link: %s",
                    vacancy_detail.alternate_url,
                )
                await self.service.update_vacancy_published_at(duplicate_hash, vacancy_detail.published_at)
                continue

            vacancy = HeadHunterVacancyCreate(
                fingerprint=fingerprint,
                vacancy_id=vacancy_detail.id,
                link=HttpsUrl(vacancy_detail.alternate_url),
                employer=vacancy_detail.employer.name,
                name=vacancy_detail.name,
                description=clear_html(vacancy_detail.description),
                salary=vacancy_detail.salary.humanize() if vacancy_detail.salary else None,
                experience=vacancy_detail.experience.name,
                schedule=vacancy_detail.schedule.name,
                work_formats=[wf.name for wf in vacancy_detail.work_format],
                key_skills=[ks.name for ks in vacancy_detail.key_skills],
                published_at=vacancy_detail.published_at,
            )
            await self.add_vacancy(vacancy)
