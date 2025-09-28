from database.models.enums import GradeEnum, ProfessionEnum, SkillEnum, SourceEnum, WorkFormatEnum
from pydantic import BaseModel, Field
from schemas.grade import GradeRead
from schemas.profession import ProfessionRead
from schemas.skill import SkillRead
from schemas.vacancy import VacanciesSummarySchema, VacancyRead
from schemas.work_format import WorkFormatRead


__all__ = [
    "ExtractSkillsRequest",
    "GradeListResponse",
    "ProfessionListResponse",
    "SkillItemResponse",
    "SkillListQuery",
    "SkillListResponse",
    "VacanciesSummaryResponse",
    "VacancyListQuery",
    "VacancyListResponse",
    "VacancyWithNeighborsQuery",
    "VacancyWithNeighborsResponse",
    "VacancyWithNeighborsSchema",
    "WorkFormatListResponse",
]


class ProfessionListResponse(BaseModel):
    professions: list[ProfessionRead]


class GradeListResponse(BaseModel):
    grades: list[GradeRead]


class WorkFormatListResponse(BaseModel):
    work_formats: list[WorkFormatRead]


class ExtractSkillsRequest(BaseModel):
    text: str


class SkillItemResponse(BaseModel):
    skill: SkillRead


class SkillListQuery(BaseModel):
    names: list[str]


class SkillListResponse(BaseModel):
    skills: list[SkillRead]


class VacancyListQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Лимит вакансий")


class VacancyWithNeighborsQuery(BaseModel):
    current_vacancy_id: int | None = Field(None)
    professions: list[ProfessionEnum] = Field([])
    grades: list[GradeEnum] = Field([])
    work_formats: list[WorkFormatEnum] = Field([])
    skills: list[SkillEnum] = Field([])
    sources: list[SourceEnum] = Field([])


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
