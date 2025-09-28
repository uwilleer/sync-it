from schemas.vacancies.base import BaseVacancy, BaseVacancyCreate, BaseVacancyRead
from schemas.vacancies.habr import HabrVacancyCreate, HabrVacancyRead
from schemas.vacancies.head_hunter import HeadHunterVacancyCreate, HeadHunterVacancyRead
from schemas.vacancies.telegram import TelegramVacancyCreate, TelegramVacancyRead
from schemas.vacancies.vacancy import VacancyRead


__all__ = [
    "BaseVacancy",
    "BaseVacancyCreate",
    "BaseVacancyRead",
    "HabrVacancyCreate",
    "HabrVacancyRead",
    "HeadHunterVacancyCreate",
    "HeadHunterVacancyRead",
    "TelegramVacancyCreate",
    "TelegramVacancyRead",
    "VacancyRead",
]
