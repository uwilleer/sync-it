from pydantic import BaseModel
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
    "VacancyListResponse",
    "VacancyWithNeighborsResponse",
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
