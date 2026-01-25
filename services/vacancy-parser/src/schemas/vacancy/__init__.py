# isort: off
from schemas.vacancy.base import BaseVacancyCreate, BaseVacancyRead
from schemas.vacancy.vacancy import VacancyFields, VacancyRead
from schemas.vacancy.habr import HabrVacancyCreate, HabrVacancyRead
from schemas.vacancy.head_hunter import HeadHunterVacancyCreate, HeadHunterVacancyRead
from schemas.vacancy.telegram import TelegramVacancyCreate, TelegramVacancyRead
# isort: on


__all__ = [
    "BaseVacancyCreate",
    "BaseVacancyRead",
    "HabrVacancyCreate",
    "HabrVacancyRead",
    "HeadHunterVacancyCreate",
    "HeadHunterVacancyRead",
    "TelegramVacancyCreate",
    "TelegramVacancyRead",
    "VacancyFields",
    "VacancyRead",
]
