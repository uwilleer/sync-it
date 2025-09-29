from collections.abc import Iterable

from async_lru import alru_cache
from common.shared.services import BaseUOWService
from database.models import Skill
from database.models.enums import SkillEnum
from schemas.skill import SkillCreate, SkillRead
from services.exceptions.skill import SkillNotFoundError
from unitofwork import UnitOfWork


__all__ = ["SkillService"]


class SkillService(BaseUOWService[UnitOfWork]):
    """Сервис для бизнес-операций с навыками."""

    @alru_cache
    async def get_skill_by_name(self, name: SkillEnum, *, by_enum: bool = False) -> SkillRead:
        if by_enum:
            enum = SkillEnum.get_safe(name)
            if not enum:
                raise SkillNotFoundError
            name = enum

        skill = await self._uow.skills.get_by_name(name)

        return SkillRead.model_validate(skill)

    async def get_skills_by_names(self, names: Iterable[str]) -> list[SkillRead]:
        enums = [SkillEnum.get_safe(name) for name in names]
        enums_filtered = [e for e in enums if e is not None]

        skills = await self._uow.skills.get_by_enums(enums_filtered)

        return [SkillRead.model_validate(s) for s in skills]

    async def get_skills(self) -> list[SkillRead]:
        skills = await self._uow.skills.get_all()

        return [SkillRead.model_validate(s) for s in skills]

    async def get_skills_by_enums(self, enums: Iterable[SkillEnum]) -> list[SkillRead]:
        skills = await self._uow.skills.get_by_enums(enums)

        return [SkillRead.model_validate(s) for s in skills]

    async def add_skill(self, skill: SkillCreate) -> SkillRead:
        skill_model = Skill(**skill.model_dump())
        created_skill = await self._uow.skills.add(skill_model)

        self.get_skill_by_name.cache_clear()

        return SkillRead.model_validate(created_skill)
