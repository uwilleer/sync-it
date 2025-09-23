# isort: off
from database.models.base import Base
from database.models.vacancy import Vacancy
# isort: on

from database.models.habr import HabrVacancy
from database.models.head_hunter import HeadHunterVacancy
from database.models.telegram import TelegramVacancy


__all__ = [
    "Base",
    "HabrVacancy",
    "HeadHunterVacancy",
    "TelegramVacancy",
    "Vacancy",
]
