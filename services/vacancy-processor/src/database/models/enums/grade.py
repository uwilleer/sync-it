from database.models.enums import BaseAliasEnum


__all__ = ["GradeEnum"]


class GradeEnum(BaseAliasEnum):
    UNKNOWN = "Неизвестно"
    INTERN = "Стажер", ("trainee", "intern")
    JUNIOR = "Junior", ("junior+", "младший")
    MIDDLE = "Middle", ("middle+", "mid", "средний", "mid+", "strong")
    SENIOR = "Senior", ("старший",)
    LEAD = "Lead", ("руководитель", "ведущий", "главный", "tech", "team")
