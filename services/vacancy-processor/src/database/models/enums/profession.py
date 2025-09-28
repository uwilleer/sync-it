# ruff: noqa: E501

from database.models.enums import BaseAliasEnum


__all__ = ["ProfessionEnum"]


# fmt: off
class ProfessionEnum(BaseAliasEnum):
    __validate_ordering__ = True

    UNKNOWN = "Неизвестно"

    ANALYST = "Аналитик", ("системный аналитик", "аналитик 1с", "бизнес-аналитик", "финансовый аналитик", "аналитик данных", "data analyst")
    BACKEND = "Backend developer", ("java-разработчик", "back-end developer", "python-разработчик", "backend-разработчик", "backend разработчик", "разработчик python", "python developer", "python разработчик", "python-инженер")
    DATA_ENGINEER = "Data Engineer", ("data engineering",)
    DATA_SCIENCE = "Data Science", ("data scientist",)
    DEVOPS = "DevOps", ("devops инженер", "devops-инженер", "devops engineer", "devops/mlops инженер")
    FRONTEND = "Frontend developer", ("frontend разработчик", "flutter-разработчик", "frontend-разработчик")
    FULLSTACK = "Fullstack developer", ("fullstack разработчик",)
    ML_ENGINEER = "ML Engineer", ("ml-инженер", "machine learning engineer", "ai-инженер")
    MOBILE = "Mobile developer", ("android разработчик", "android developer", "ios developer", "ios разработчик")
    QA_ENGINEER = "QA Engineer", ("fullstack qa", "qa automation engineer", "тестировщик", "qa инженер", "qa fullstack")
    SYSTEM_ADMINISTRATOR = "Системный администратор"
    TECH_LEAD = "Tech Lead"
    UX_UX_DESIGNER = "UX/UI-дизайнер", ("ux/ui дизайнер",)

    __ignore_patterns__ = (
        "маркетолог", "продаж", "менеджер", "маркетинг", "бухгалтер", "seo-специалист", "контролер", "юрист"
    )
# fmt: on
