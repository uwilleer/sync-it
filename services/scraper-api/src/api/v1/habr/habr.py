from typing import Annotated

from api.v1.habr.schemas import HabrVacanciesQuery, HabrVacancyDetailedResponse, HabrVacancyListResponse
from clients import habr_client
from common.logger import get_logger
from fastapi import APIRouter, Query


logger = get_logger(__name__)

router = APIRouter()


@router.get("/vacancies")
async def get_vacancies(query: Annotated[HabrVacanciesQuery, Query()]) -> HabrVacancyListResponse:
    vacancy_ids = await habr_client.get_newest_vacancies_ids(query.date_gte)

    return HabrVacancyListResponse(vacancies=vacancy_ids)


@router.get("/vacancies/{vacancy_id}")
async def get_vacancy(vacancy_id: int) -> HabrVacancyDetailedResponse:
    vacancy = await habr_client.get_vacancy_by_id(vacancy_id)

    return HabrVacancyDetailedResponse(vacancy=vacancy)
