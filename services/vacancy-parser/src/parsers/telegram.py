from collections.abc import Iterable

from clients import telegram_client
from common.logger import get_logger
from common.shared.schemas import HttpsUrl
from parsers.base import BaseParser
from parsers.schemas import TelegramChannelUrl
from schemas.vacancies import TelegramVacancyCreate
from unitofwork import UnitOfWork
from utils import generate_fingerprint

from services import TelegramVacancyService


__all__ = ["TelegramParser"]


logger = get_logger(__name__)


class TelegramParser(BaseParser[TelegramVacancyService]):
    MIN_VACANCY_TEXT_LENGTH = 600

    def __init__(
        self, uow: UnitOfWork, service: TelegramVacancyService, channel_links: Iterable[TelegramChannelUrl]
    ) -> None:
        super().__init__(uow, service)
        self.channel_links = channel_links

    async def parse(self) -> None:
        logger.info("Starting Telegram parser")

        for channel_link in self.channel_links:
            try:
                await self._process_channel(channel_link)
            except Exception as e:
                logger.exception("Error processing channel '%s'", channel_link, exc_info=e)

    async def _process_channel(self, channel_link: TelegramChannelUrl) -> None:
        logger.debug("Start parsing channel '%s'", channel_link)

        last_message_id = await self.service.get_last_message_id(channel_link)
        logger.debug("Last message id for channel '%s' is %s", channel_link, last_message_id)

        newest_messages = await telegram_client.get_newest_messages(channel_link.channel_username, last_message_id)

        if not newest_messages:
            logger.debug("No new messages for channel '%s'", channel_link)
            return

        logger.debug("Got %s new messages", len(newest_messages))

        vacancies: list[TelegramVacancyCreate] = []
        for message in newest_messages:
            if len(message.text) < self.MIN_VACANCY_TEXT_LENGTH:
                continue
            if "#резюме" in message.text.lower():
                continue

            fingerprint = generate_fingerprint(message.text)
            duplicate = await self.service.find_duplicate_vacancy_by_fingerprint(fingerprint)
            if duplicate:
                logger.debug(
                    "Found duplicate vacancy. New vacancy link: %s/%s, Existing vacancy link: %s",
                    channel_link,
                    message.id,
                    duplicate.link,
                )
                await self.service.update_vacancy_published_at(duplicate.hash, message.datetime)
                continue

            vacancy_create = TelegramVacancyCreate(
                fingerprint=fingerprint,
                link=HttpsUrl(f"{channel_link}/{message.id}"),
                channel_username=channel_link.channel_username,
                message_id=message.id,
                published_at=message.datetime,
                data=message.text,
            )
            vacancies.append(vacancy_create)

        new_vacancies = await self._get_new_vacancies(vacancies)

        if not vacancies or not new_vacancies:
            logger.debug("No new vacancies for channel '%s'", channel_link)
            return

        for new_vacancy in new_vacancies:
            await self.service.add_vacancy(new_vacancy)
            logger.debug("Added vacancy: %s", new_vacancy.link)

    async def _get_new_vacancies(self, vacancies: list[TelegramVacancyCreate]) -> list[TelegramVacancyCreate]:
        vacancy_hashes = [v.hash for v in vacancies]
        existing_hashes = await self.service.get_existing_hashes(vacancy_hashes)

        return [v for v in vacancies if v.hash not in existing_hashes]
