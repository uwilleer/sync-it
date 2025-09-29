import asyncio
from datetime import timedelta

from celery_app import app
from common.logger import get_logger
from common.redis.decorators.singleton import singleton
from constants.telegram import channel_links
from parsers import HeadHunterParser, TelegramParser
from parsers.habr import HabrParser
from unitofwork import UnitOfWork

from services import HabrVacancyService, HeadHunterVacancyService, TelegramVacancyService


__all__ = ["parse_vacancies"]


logger = get_logger(__name__)


@app.task(name="parse_vacancies")
@singleton(timedelta(minutes=60))
def parse_vacancies() -> None:
    """Основная задача Celery для запуска всех парсеров."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_all_parsers())


async def run_all_parsers() -> None:
    """Запускает все парсеры параллельно и обрабатывает результаты."""
    logger.info("Run all parsers")

    tasks = [
        parse_telegram_vacancies(),
        parse_head_hunter_vacancies(),
        parse_habr_vacancies(),
    ]

    for coro in tasks:
        try:
            await coro
        except Exception as e:
            logger.exception("Error running parser", exc_info=e)


async def parse_telegram_vacancies() -> None:
    async with UnitOfWork() as uow:
        service = TelegramVacancyService(uow)
        parser = TelegramParser(uow, service, channel_links)
        await parser.parse()
        await uow.commit()


async def parse_head_hunter_vacancies() -> None:
    async with UnitOfWork() as uow:
        service = HeadHunterVacancyService(uow)
        parser = HeadHunterParser(uow, service)
        await parser.parse()
        await uow.commit()


async def parse_habr_vacancies() -> None:
    async with UnitOfWork() as uow:
        service = HabrVacancyService(uow)
        parser = HabrParser(uow, service)
        await parser.parse()
        await uow.commit()
