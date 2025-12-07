from database.models.enums import GradeEnum, ProfessionEnum, SkillEnum, SourceEnum, WorkFormatEnum
from pydantic import BaseModel, ConfigDict, Field
from schemas.grade import GradeRead
from schemas.profession import ProfessionRead
from schemas.skill import SkillRead
from schemas.vacancy import VacanciesSummarySchema, VacancyRead
from schemas.work_format import WorkFormatRead


class ProfessionListResponse(BaseModel):
    professions: list[ProfessionRead]


class GradeListResponse(BaseModel):
    grades: list[GradeRead]


class WorkFormatListResponse(BaseModel):
    work_formats: list[WorkFormatRead]


class ExtractSkillsRequest(BaseModel):
    text: str

    model_config = ConfigDict(extra="forbid")


class SkillItemResponse(BaseModel):
    skill: SkillRead


class SkillListQuery(BaseModel):
    names: list[str]

    model_config = ConfigDict(extra="forbid")


class SkillListResponse(BaseModel):
    skills: list[SkillRead]


class VacancyListQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Лимит вакансий")

    model_config = ConfigDict(extra="forbid")


class VacancyWithNeighborsBody(BaseModel):
    current_vacancy_id: int | None = Field(None)
    professions: list[ProfessionEnum] = Field([])
    grades: list[GradeEnum] = Field([])
    work_formats: list[WorkFormatEnum] = Field([])
    skills: list[SkillEnum] = Field([])
    sources: list[SourceEnum] = Field([])

    model_config = ConfigDict(extra="forbid")


class VacancyListResponse(BaseModel):
    vacancies: list[VacancyRead]


class VacancyWithNeighborsSchema(BaseModel):
    prev_id: int | None
    next_id: int | None
    vacancy: VacancyRead | None


class VacancyWithNeighborsResponse(BaseModel):
    result: VacancyWithNeighborsSchema


class VacanciesSummaryResponse(BaseModel):
    result: VacanciesSummarySchema
