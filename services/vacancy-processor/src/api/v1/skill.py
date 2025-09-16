from typing import Annotated

from api.depedencies import get_skill_service
from api.v1.schemas import ExtractSkillsRequest, SkillItemResponse, SkillListResponse
from clients import gpt_client
from database.models.enums import SkillEnum
from fastapi import APIRouter, Depends
from schemas.skill import SkillRead
from utils.extractor import VacancyExtractor
from utils.prompter import make_resume_prompt

from services import SkillService


__all__ = ["router"]


router = APIRouter()


@router.get("")
async def get_skills(service: Annotated[SkillService, Depends(get_skill_service)]) -> SkillListResponse:
    """Возвращает актуальные скиллы."""
    skills = await service.get_skills()

    return SkillListResponse(skills=[SkillRead.model_validate(s) for s in skills])


@router.get("/{name}")
async def get_by_name(service: Annotated[SkillService, Depends(get_skill_service)], name: str) -> SkillItemResponse:
    """Возвращает скилл по его названию (включая вариации)"""
    skill = await service.get_skill_by_name(name, by_enum=True)

    return SkillItemResponse(skill=SkillRead.model_validate(skill))


@router.post("/extract")
async def extract_skills(
    request: ExtractSkillsRequest,
    service: Annotated[SkillService, Depends(get_skill_service)],
) -> SkillListResponse:
    prompt = make_resume_prompt(request.text)
    completion = await gpt_client.get_completion(prompt)
    extractor = VacancyExtractor()
    skill_enums = extractor.extract_skills(completion)
    skills = await service.get_skills_by_enums(s for s in skill_enums if s != SkillEnum.UNKNOWN)

    return SkillListResponse(skills=skills)
