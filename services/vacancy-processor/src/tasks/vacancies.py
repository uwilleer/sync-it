from datetime import timedelta

from celery_app import app
from common.redis.decorators.singleton import singleton
from common.shared.utils import run_async
from unitofwork import UnitOfWork
from utils.extractor import VacancyExtractor
from utils.processor import VacancyProcessor

from services import GradeService, ProfessionService, SkillService, VacancyService, WorkFormatService


__all__ = ["process_vacancies"]


@app.task(name="process_vacancies")
@singleton(timedelta(minutes=60))
def process_vacancies() -> None:
    run_async(async_process_vacancies())


async def async_process_vacancies() -> None:
    extractor = VacancyExtractor()

    async with UnitOfWork() as uow:
        vacancy_service = VacancyService(uow)
        grade_service = GradeService(uow)
        profession_service = ProfessionService(uow)
        work_format_service = WorkFormatService(uow)
        skill_service = SkillService(uow)
        processor = VacancyProcessor(
            uow,
            extractor,
            vacancy_service,
            grade_service,
            profession_service,
            work_format_service,
            skill_service,
        )

        vacancies_to_process = await processor.start()
        while vacancies_to_process != 0:
            vacancies_to_process = await processor.start()

        await uow.commit()
