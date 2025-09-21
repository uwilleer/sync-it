from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


__all__ = [
    "VacancyActionEnum",
    "VacancyCallback",
]


class VacancyActionEnum(StrEnum):
    SHOW_VACANCY = "show_vacancy"
    SELECT_SKILLS = "select_skills"


class VacancyCallback(CallbackData, prefix="vacancy"):
    action: VacancyActionEnum

    vacancy_id: int | None = None

    skill_id: int | None = None
    skill_name: str | None = None
