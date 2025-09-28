from database.models.enums import BaseAliasEnum


__all__ = ["GradeEnum"]


class GradeEnum(BaseAliasEnum):
    UNKNOWN = "Неизвестно"
    INTERN = "Стажер", ("trainee",)
    JUNIOR = "Junior", ("junior+", "младший")
    MIDDLE = "Middle", ("middle+", "mid", "средний", "mid+")
    SENIOR = "Senior", ("старший",)
    LEAD = "Lead", ("руководитель", "ведущий", "главный", "tech")
