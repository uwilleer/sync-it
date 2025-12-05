from typing import Annotated

from api.dependencies import get_vacancy_service
from api.v1.schemas import VacanciesListQuery, VacancyListResponse, VacancyProcessedBody, VacancyProcessedResponse
from fastapi import APIRouter, Body, Depends, Query

from services import VacancyService


__all__ = ["router"]


router = APIRouter()


@router.get("/vacancies")
async def get_vacancies(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
    query: Annotated[VacanciesListQuery, Query()],
) -> VacancyListResponse:
    """Возвращает последние актуальные вакансии."""
    vacancies = await service.get_recent_vacancies(limit=query.limit)

    return VacancyListResponse(vacancies=vacancies)


@router.post("/vacancies/mark-processed")
async def mark_vacancies_as_processed(
    data: Annotated[VacancyProcessedBody, Body()],
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
) -> VacancyProcessedResponse:
    await service.mark_vacancies_as_processed(data.hashes)

    return VacancyProcessedResponse(count=len(data.hashes))
