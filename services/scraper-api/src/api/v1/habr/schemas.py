from pydantic import BaseModel
from schemas import DateGTEUTCMixin, HabrDetailedVacancySchema


__all__ = [
    "HabrVacanciesQuery",
    "HabrVacancyDetailedResponse",
    "HabrVacancyListResponse",
]


class HabrVacanciesQuery(DateGTEUTCMixin):
    pass


class HabrVacancyListResponse(BaseModel):
    vacancies: list[int]


class HabrVacancyDetailedResponse(BaseModel):
    vacancy: HabrDetailedVacancySchema
