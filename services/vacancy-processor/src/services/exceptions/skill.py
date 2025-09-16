from services.exceptions.base import NotFoundError


__all__ = ["SkillNotFoundError"]


class SkillNotFoundError(NotFoundError):
    DETAIL = "Навык не найден"
