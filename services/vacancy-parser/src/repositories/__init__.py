# isort: off
from repositories.base import BaseVacancyRepository
from repositories.vacancy import VacancyRepository
# isort: on

from repositories.head_hunter import HeadHunterVacancyRepository
from repositories.telegram import TelegramVacancyRepository


__all__ = [
    "BaseVacancyRepository",
    "HeadHunterVacancyRepository",
    "TelegramVacancyRepository",
    "VacancyRepository",
]
