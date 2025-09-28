from typing import Annotated

from api.depedencies import get_vacancy_service
from api.v1.schemas import (
    VacanciesSummaryResponse,
    VacancyListQuery,
    VacancyListResponse,
    VacancyWithNeighborsQuery,
    VacancyWithNeighborsResponse,
    VacancyWithNeighborsSchema,
)
from common.logger import get_logger
from fastapi import APIRouter, Depends, Query

from services import VacancyService


__all__ = ["router"]


logger = get_logger(__name__)
router = APIRouter()


@router.get("")
async def get_vacancies(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
    query: Annotated[VacancyListQuery, Query()],
) -> VacancyListResponse:
    """Получить список актуальных вакансий, подходящих под заданные фильтры."""
    vacancies = await service.get_vacancies(query.limit)

    return VacancyListResponse(vacancies=vacancies)


@router.get("/match")
async def get_vacancy_with_neighbors(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
    query: Annotated[VacancyWithNeighborsQuery, Query()],
) -> VacancyWithNeighborsResponse:
    prev_id, vacancy, next_id = await service.get_vacancy_with_neighbors(
        query.current_vacancy_id,
        query.professions,
        query.grades,
        query.work_formats,
        query.skills,
        query.sources,
    )

    result = VacancyWithNeighborsSchema(
        prev_id=prev_id,
        next_id=next_id,
        vacancy=vacancy,
    )

    return VacancyWithNeighborsResponse(result=result)


@router.get("/summary")
async def get_summary_vacancies(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
) -> VacanciesSummaryResponse:
    summary = await service.get_summary_vacancies()

    return VacanciesSummaryResponse(result=summary)
