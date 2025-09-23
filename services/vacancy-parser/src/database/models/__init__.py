# isort: off
from database.models.base import Base
from database.models.vacancy.vacancy import Vacancy
# isort: on

from database.models.vacancy.habr import HabrVacancy
from database.models.vacancy.head_hunter import HeadHunterVacancy
from database.models.vacancy.telegram import TelegramVacancy


__all__ = ["Base", "HabrVacancy", "HeadHunterVacancy", "TelegramVacancy", "Vacancy",]
