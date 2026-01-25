from datetime import datetime
from typing import TYPE_CHECKING, Optional

from database.models import Base
from database.models.tables import vacancy_grades_table, vacancy_skills_table, vacancy_work_formats_table
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import Grade, Profession, Skill, WorkFormat


class Vacancy(Base):
    """Вакансия"""

    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID вакансии")
    source: Mapped[str] = mapped_column(String(16), index=True, doc="Источник вакансии")
    hash: Mapped[str] = mapped_column(String(32), unique=True, doc="Хеш вакансии")
    link: Mapped[str] = mapped_column(String(256), doc="Ссылка на вакансию")

    company_name: Mapped[str | None] = mapped_column(String(128), doc="Название компании")
    salary: Mapped[str | None] = mapped_column(String(96), doc="Зарплата")
    workplace_description: Mapped[str | None] = mapped_column(Text, doc="Описание места работы")
    responsibilities: Mapped[str | None] = mapped_column(Text, doc="Обязанности")
    requirements: Mapped[str | None] = mapped_column(Text, doc="Требования")
    conditions: Mapped[str | None] = mapped_column(Text, doc="Условия работы")

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, doc="Дата публикации вакансии")

    profession_id: Mapped[int | None] = mapped_column(
        ForeignKey("professions.id", ondelete="CASCADE"), doc="ID профессии"
    )
    profession: Mapped[Optional["Profession"]] = relationship(back_populates="vacancies", doc="Профессия")

    grades: Mapped[list["Grade"]] = relationship(
        secondary=vacancy_grades_table, back_populates="vacancies", doc="Уровни вакансии"
    )
    work_formats: Mapped[list["WorkFormat"]] = relationship(
        secondary=vacancy_work_formats_table, back_populates="vacancies", doc="Форматы работы"
    )
    skills: Mapped[list["Skill"]] = relationship(
        secondary=vacancy_skills_table, back_populates="vacancies", doc="Навыки, требуемые для вакансии"
    )

    __table_args__ = (
        Index("idx_vacancy_published_at_id", "published_at", "id"),
        Index("idx_vacancy_source_link", "source", "link", unique=True),
        Index("idx_vacancy_profession_id", "profession_id"),
        Index("idx_vacancy_source_published_at", "source", "published_at"),
    )
