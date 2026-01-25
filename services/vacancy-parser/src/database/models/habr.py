from database.models import Vacancy
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


__all__ = ["HabrVacancy"]


class HabrVacancy(Vacancy):
    __tablename__ = "habr_vacancies"

    id: Mapped[int] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True, doc="ID вакансии")
    external_id: Mapped[int] = mapped_column(Integer, doc="Внешний ID вакансии на Habr")

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": "habr",
    }
