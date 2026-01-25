from enum import StrEnum


class PreferencesCategoryCodeEnum(StrEnum):
    """Перечисление категорий предпочтений пользователя.

    Используется для классификации предпочтений пользователя
    в модели UserPreference.
    """

    PROFESSION = "profession"
    """Профессия пользователя."""

    SKILL = "skill"
    """Навык пользователя."""

    GRADE = "grade"
    """Грейд пользователя."""

    WORK_FORMAT = "work_format"
    """Формат работы (удалёнка, офис и т.д.)."""

    SOURCE = "source"
    """Источник вакансий (Telegram, HeadHunter, Habr и т.д.)."""
