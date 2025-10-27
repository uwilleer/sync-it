from typing import Annotated

from api.depedencies import get_vacancy_service
from api.v1.schemas import (
    VacanciesSummaryResponse,
)
from common.logger import get_logger
from fastapi import APIRouter, Depends

from services import VacancyService


__all__ = ["router"]


logger = get_logger(__name__)
router = APIRouter()


@router.get("/summary")
async def get_summary_vacancies(
    service: Annotated[VacancyService, Depends(get_vacancy_service)],
) -> VacanciesSummaryResponse:
    summary = await service.get_summary_vacancies()

    return VacanciesSummaryResponse(result=summary)
