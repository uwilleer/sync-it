from typing import TYPE_CHECKING

from database.models import Base
from database.models.enums import ProfessionEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import Vacancy


__all__ = ["Profession"]


class Profession(Base):
    """Профессия"""

    __tablename__ = "professions"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID профессии")
    name: Mapped[ProfessionEnum] = mapped_column(String(32), unique=True, doc="Название профессии")

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="profession", doc="Список вакансий данной профессии"
    )
