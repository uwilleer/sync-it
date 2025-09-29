from datetime import UTC, datetime

from bs4 import BeautifulSoup
from common.logger import get_logger
from parsers import BaseParser
from parsers.exceptions import ParserBlockNotFoundError
from schemas import HabrDetailedVacancySchema


__all__ = ["HabrParser"]


logger = get_logger(__name__)


class HabrParser(BaseParser):
    @staticmethod
    def parse_detailed_vacancy(html_content: str, vacancy_id: int) -> HabrDetailedVacancySchema:
        soup = BeautifulSoup(html_content, "html.parser")

        company_name_block = soup.select_one("div.company_name")
        if company_name_block is None:
            raise ParserBlockNotFoundError

        # Не у каждой компании есть этот блок
        company_description_block = soup.select_one("div.company_about")

        description_block = soup.select_one("article.vacancy-show")
        if description_block is None:
            raise ParserBlockNotFoundError

        blocks_to_remove = [
            "div.vacancy-company__footer",
            "div.similar_vacancies",
            "div.mq-mobile-only",
            "div.opposing-items",
        ]

        for block in blocks_to_remove:
            item = description_block.select_one(block)
            if item:
                item.decompose()
            else:
                logger.warning("Block %s not found", block)

        time_tag = soup.select_one("div.vacancy-header__date time")
        if time_tag is None:
            raise ParserBlockNotFoundError

        iso_str = str(time_tag["datetime"])  # '2025-09-28T12:27:09+03:00'

        dt_local = datetime.fromisoformat(iso_str)
        dt_utc = dt_local.astimezone(UTC)

        text = f"Название компании: {company_name_block.get_text(strip=True)}\n"
        if company_description_block:
            text += f"Информация о компании: {company_description_block.get_text(strip=True)}\n"

        text += f"Описание вакансии: {description_block.get_text(strip=True, separator='\n')}"

        return HabrDetailedVacancySchema(id=vacancy_id, text=text, datetime=dt_utc)
