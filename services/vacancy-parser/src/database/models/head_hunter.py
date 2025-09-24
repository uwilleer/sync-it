from database.models import Vacancy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


__all__ = ["HeadHunterVacancy"]


class HeadHunterVacancy(Vacancy):
    __tablename__ = "head_hunter_vacancies"

    id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"), primary_key=True)

    vacancy_id: Mapped[int] = mapped_column()

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": "head_hunter",
    }
