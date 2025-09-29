import asyncio
from itertools import starmap

from clients import gpt_client, vacancy_client
from clients.schemas import VacancySchema
from common.logger import get_logger
from schemas.vacancy import VacancyCreate
from sqlalchemy.exc import IntegrityError
from unitofwork import UnitOfWork
from utils.extractor import VacancyExtractor
from utils.prompter import make_vacancy_prompt

from services import (
    GradeService,
    ProfessionService,
    SkillService,
    VacancyService,
    WorkFormatService,
)


__all__ = ["VacancyProcessor"]


logger = get_logger(__name__)


class VacancyProcessor:
    def __init__(
        self,
        uow: UnitOfWork,
        vacancy_extractor: VacancyExtractor,
        vacancy_service: VacancyService,
        grade_service: GradeService,
        profession_service: ProfessionService,
        work_format_service: WorkFormatService,
        skill_service: SkillService,
    ) -> None:
        self.uow = uow
        self.vacancy_extractor = vacancy_extractor
        self.vacancy_service = vacancy_service
        self.grade_service = grade_service
        self.profession_service = profession_service
        self.work_format_service = work_format_service
        self.skill_service = skill_service

    async def start(self) -> None:
        logger.debug("Start processing vacancies")
        vacancies = await vacancy_client.get_vacancies()
        existing_vacancies = await self.uow.vacancies.get_existing_hashes([v.hash for v in vacancies])
        vacancies_to_process = [v for v in vacancies if v.hash not in existing_vacancies]
        logger.debug("Got %s new vacancies", len(vacancies_to_process))

        prompts = [make_vacancy_prompt(vacancy.data) for vacancy in vacancies_to_process]
        process_prompts_task = list(starmap(self._process_prompt, zip(prompts, vacancies_to_process, strict=True)))

        vacancies_to_delete: list[VacancySchema] = []

        results = await asyncio.gather(*process_prompts_task, return_exceptions=True)
        for processed_vacancy, result in zip(vacancies_to_process, results, strict=True):
            if isinstance(result, BaseException):
                logger.error("Failed to process vacancy %s", processed_vacancy.link, exc_info=result)
                continue
            if result is None:
                logger.debug("Not a vacancy: %s", processed_vacancy.link)
                vacancies_to_delete.append(processed_vacancy)
                continue

            extracted_vacancy, vacancy = result

            try:
                await self._process_vacancy(extracted_vacancy, vacancy)
                vacancies_to_delete.append(processed_vacancy)
            except IntegrityError as e:
                logger.warning("Duplicate vacancy: %s", processed_vacancy.link, exc_info=e)
                vacancies_to_delete.append(processed_vacancy)

        # Сохраним вакансии, перед их удалением
        await self.uow.commit()

        if vacancies_to_delete:
            logger.debug("Deleting %s vacancies", len(vacancies_to_delete))
            delete_vacancies_tasks = [vacancy_client.delete(vacancy) for vacancy in vacancies_to_delete]
            await asyncio.gather(*delete_vacancies_tasks)

    async def _process_prompt(
        self, prompt: str, vacancy: VacancySchema
    ) -> tuple[VacancyExtractor, VacancySchema] | None:
        completion = await gpt_client.get_completion(prompt)

        bad_completions = (
            "Не вакансия",
            "It seems that this video doesn't have a transcript, please try another video",
        )
        if any(bad_completion in completion for bad_completion in bad_completions):
            logger.debug("Not a vacancy: %s", vacancy.link)
            return None

        extracted_vacancy = self.vacancy_extractor.extract(completion)
        if not self.vacancy_extractor.is_valid_vacancy(extracted_vacancy):
            return None

        return extracted_vacancy, vacancy

    async def _process_vacancy(self, extracted_vacancy: VacancyExtractor, vacancy: VacancySchema) -> None:
        logger.debug("Processing vacancy: %s", vacancy.link)

        profession_task = self.profession_service.get_profession_by_name(extracted_vacancy.profession)
        grades_tasks = [self.grade_service.get_grade_by_name(name) for name in extracted_vacancy.grades]
        skills_tasks = [self.skill_service.get_skill_by_name(name) for name in extracted_vacancy.skills]
        wf_tasks = [self.work_format_service.get_work_format_by_name(name) for name in extracted_vacancy.work_formats]

        profession = await profession_task
        grades = [g for g in await asyncio.gather(*grades_tasks) if g]
        skills = [s for s in await asyncio.gather(*skills_tasks) if s]
        work_formats = [w for w in await asyncio.gather(*wf_tasks) if w]

        max_salary_length = 96
        if extracted_vacancy.salary and len(extracted_vacancy.salary) > max_salary_length:
            logger.warning(
                "Salary length >%s",
                max_salary_length,
                extra={"salary": extracted_vacancy.salary},
            )
            return

        vacancy_create = VacancyCreate(
            source=vacancy.source,
            published_at=vacancy.published_at,
            hash=vacancy.hash,
            link=vacancy.link,
            company_name=extracted_vacancy.company_name,
            profession_id=profession.id if profession else None,
            salary=extracted_vacancy.salary,
            workplace_description=extracted_vacancy.workplace_description,
            responsibilities=extracted_vacancy.responsibilities,
            requirements=extracted_vacancy.requirements,
            conditions=extracted_vacancy.conditions,
        )

        await self.vacancy_service.add_vacancy(vacancy_create, grades, work_formats, skills)
