from schemas.vacancies.base import BaseVacancy, BaseVacancyCreate, BaseVacancyRead
from schemas.vacancies.head_hunter import HeadHunterVacancyCreate, HeadHunterVacancyRead
from schemas.vacancies.telegram import TelegramVacancyCreate, TelegramVacancyRead
from schemas.vacancies.vacancy import VacancyRead


__all__ = [
    "BaseVacancy",
    "BaseVacancyCreate",
    "BaseVacancyRead",
    "HeadHunterVacancyCreate",
    "HeadHunterVacancyRead",
    "TelegramVacancyCreate",
    "TelegramVacancyRead",
    "VacancyRead",
]
