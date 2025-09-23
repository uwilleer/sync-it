# isort: off
from services.base import BaseVacancyService
from services.vacancy import VacancyService
# isort: on

from services.head_hunter import HeadHunterVacancyService
from services.telegram import TelegramVacancyService


__all__ = [
    "BaseVacancyService",
    "HeadHunterVacancyService",
    "TelegramVacancyService",
    "VacancyService",
]
