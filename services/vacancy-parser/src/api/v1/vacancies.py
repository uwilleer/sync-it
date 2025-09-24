from typing import Annotated

from api.dependencies import get_vacancy_service
from api.schemas import VacanciesListQuery
from api.v1.schemas import VacancyListResponse, VacancyProcessedResponse
from fastapi import APIRouter, Depends

from services import VacancyService


__all__ = ["router"]


router = APIRouter()


@router.get("/vacancies")
async def get_vacancies(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
    query: Annotated[VacanciesListQuery, Depends(VacanciesListQuery)],
) -> VacancyListResponse:
    """Возвращает последние актуальные вакансии."""
    vacancies = await service.get_recent_vacancies(limit=query.limit)

    return VacancyListResponse(vacancies=vacancies)


@router.post("/vacancies/{vacancy_hash}")
async def mark_vacancy_as_processed(
    vacancy_hash: str,
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
) -> VacancyProcessedResponse:
    is_processed = await service.mark_as_processed(vacancy_hash)

    await service.commit()

    return VacancyProcessedResponse(is_processed=is_processed)
