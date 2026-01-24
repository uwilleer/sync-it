from typing import TYPE_CHECKING

from database.models import Base
from database.models.tables import vacancy_skills_table
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import Vacancy


__all__ = ["Skill"]


class Skill(Base):
    """Навык"""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID навыка")
    name: Mapped[str] = mapped_column(String(32), unique=True, doc="Название навыка")

    vacancies: Mapped[list["Vacancy"]] = relationship(
        secondary=vacancy_skills_table,
        back_populates="skills",
        passive_deletes=True,
        doc="Список вакансий, связанных с данным навыком",
    )
