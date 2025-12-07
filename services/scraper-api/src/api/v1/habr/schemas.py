from pydantic import BaseModel, ConfigDict
from schemas import DateGTEUTCMixin, HabrDetailedVacancySchema


class HabrVacanciesQuery(DateGTEUTCMixin):
    model_config = ConfigDict(extra="forbid")


class HabrVacancyListResponse(BaseModel):
    vacancies: list[int]


class HabrVacancyDetailedResponse(BaseModel):
    vacancy: HabrDetailedVacancySchema
